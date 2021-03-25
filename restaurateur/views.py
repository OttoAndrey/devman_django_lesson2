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
from geopy.distance import distance

from star_burger.settings import YA_GEOCODER_API_KEY
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


def get_available_restaurants(order):
    """Returns a list of restaurants that can fulfill an order."""
    restaurants = Restaurant.objects.all()
    available_restaurants = []
    order_items = set(order.items.values_list('product__name', flat=True))
    for restaurant in restaurants:
        restaurant_items = (
            restaurant.menu_items
            .filter(availability=True)
            .values_list('product__name', flat=True)
        )
        if order_items.issubset(restaurant_items):
            available_restaurants.append(restaurant)
    return available_restaurants


def get_distance_between_restaurants_and_order(order, restaurants):
    """Calculates the distance between restaurants and the order address."""
    restaurants_with_distance = {}
    order_coordinates = get_coordinates(order)

    for restaurant in restaurants:
        rest_coordinates = get_coordinates(restaurant)
        distance_between_restaurant_and_order = round(
            distance(rest_coordinates, order_coordinates).km,
            ndigits=3,
        )
        restaurants_with_distance[restaurant] = (
            distance_between_restaurant_and_order
        )
    sorted(restaurants_with_distance.items(), key=lambda dist: dist[1])

    return restaurants_with_distance


def get_coordinates(instance):
    """Returns coordinates of object."""
    if (coordinate_name := f'{instance.__str__()}_coordinates') in cache:
        coordinates = cache.get(coordinate_name)
    else:
        coordinates = fetch_coordinates(YA_GEOCODER_API_KEY, instance.address)
        cache.set(coordinate_name, coordinates, timeout=864000)
    return coordinates[1], coordinates[0]


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.get_total_price()

    for order in orders:
        available_restaurants = get_available_restaurants(order)
        order.available_restaurants_with_distance = (
            get_distance_between_restaurants_and_order(
                order,
                available_restaurants,
            )
        )

    return render(
        request,
        template_name='order_items.html',
        context={'order_items': orders},
    )


def fetch_coordinates(apikey, place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = places_found[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat
