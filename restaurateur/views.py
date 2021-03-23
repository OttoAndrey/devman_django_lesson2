from collections import Counter

import requests
from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy import distance

from StarBurger.settings import YA_GEOCODER_API_KEY
from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:
        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.get_total_price()

    for order in orders:
        order_items = order.items.all()
        available_restaurants_for_each_product_in_order = []
        available_restaurants_for_order = []
        available_restaurants_with_distance = {}
        order.available_restaurants_with_distance = {}

        for order_item in order_items:
            available_restaurants_for_each_product_in_order.append([rmi.restaurant for rmi in RestaurantMenuItem.objects
                                                                   .filter(product=order_item.product)
                                                                   .filter(availability=True)])

        if len(available_restaurants_for_each_product_in_order) == 0:
            order.available_restaurants_with_distance = {'Нет доступных ресторанов': '0'}
            continue

        for available_restaurants in available_restaurants_for_each_product_in_order:
            if len(available_restaurants) == 0:
                order.available_restaurants_with_distance = {'Нет доступных ресторанов': '0'}
                break

        if order.available_restaurants_with_distance == {'Нет доступных ресторанов': '0'}:
            break

        all_restaurants = []
        [all_restaurants.extend(available_restaurant) for available_restaurant in
         available_restaurants_for_each_product_in_order]

        all_restaurants_with_count = dict(Counter(all_restaurants))

        for restaurant, restaurant_count in all_restaurants_with_count.items():
            if not restaurant_count == len(available_restaurants_for_each_product_in_order):
                continue
            available_restaurants_for_order.append(restaurant)

        if len(available_restaurants_for_order) == 0:
            order.available_restaurants_with_distance = {'Нет доступных ресторанов': '0'}
            continue

        if f'{order.__str__()}_coordinates' in cache:
            coordinates = cache.get(f'{order.__str__()}_coordinates')
        else:
            coordinates = fetch_coordinates(YA_GEOCODER_API_KEY, order.address)
            cache.set(f'{order.__str__()}_coordinates', coordinates, timeout=864000)
        order_coordinates = (coordinates[1], coordinates[0])

        for rest in available_restaurants_for_order:
            if f'{rest.name}_coordinates' in cache:
                coordinates = cache.get(f'{rest.name}_coordinates')
            else:
                coordinates = fetch_coordinates(YA_GEOCODER_API_KEY, rest.address)
                cache.set(f'{rest.name}_coordinates', coordinates, timeout=864000)
            rest_coordinates = (coordinates[1], coordinates[0])
            distance_between_rest_and_order = round(distance.distance(rest_coordinates, order_coordinates).km, 3)
            available_restaurants_with_distance[rest] = distance_between_rest_and_order

        order.available_restaurants_with_distance = dict(sorted(available_restaurants_with_distance.items(),
                                                                key=lambda dist: dist[1]))

    return render(request, template_name='order_items.html', context={
        'order_items': orders,
    })


def fetch_coordinates(apikey, place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = places_found[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat
