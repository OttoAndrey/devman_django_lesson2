from unittest.mock import patch

from django.contrib.auth.models import User
from django.db.models import Prefetch
from django.test import TestCase
from django.urls import reverse

from foodcartapp.factories import (
    OrderWithProductsFactory,
    ProductCategoryFactory,
    ProductFactory,
    RestaurantWithAllAvailabilityProductsFactory,
    RestaurantWithoutAllAvailabilityProductsFactory,
)
from foodcartapp.models import Order, Restaurant, RestaurantMenuItem
from restaurateur.factories import SuperUserFactory
from restaurateur.views import (
    get_available_restaurants,
    get_distance_between_restaurants_and_order,
)


class ServicesTests(TestCase):

    def setUp(self):
        SuperUserFactory()
        ProductCategoryFactory.create_batch(3)
        ProductFactory.create_batch(2)
        OrderWithProductsFactory()
        RestaurantWithoutAllAvailabilityProductsFactory()
        self.possible_restaurant = (
            RestaurantWithAllAvailabilityProductsFactory()
        )

    def test_get_available_restaurants(self):
        order = Order.objects.last()
        restaurants = Restaurant.objects.prefetch_related(
            Prefetch(
                'menu_items',
                RestaurantMenuItem.objects
                .filter(availability=True)
                .select_related('product'),
            )
        )
        available_restaurants = get_available_restaurants(order, restaurants)

        self.assertEqual(Restaurant.objects.count(), 2)
        self.assertEqual(len(available_restaurants), 1)
        self.assertEqual(
            available_restaurants[0].name,
            self.possible_restaurant.name,
        )

    @patch('restaurateur.views.get_coordinates')
    def test_get_distance_between_restaurants_and_order(
            self,
            mock_get_coordinates,
    ):
        get_coordinates = mock_get_coordinates()
        get_coordinates.return_value = ('55.7522', '37.6156')
        order = Order.objects.last()
        restaurants = Restaurant.objects.all()
        available_restaurants = get_available_restaurants(order, restaurants)
        restaurants_with_distance = get_distance_between_restaurants_and_order(
            order,
            available_restaurants,
        )

        self.assertEqual(type(restaurants_with_distance), dict)
        self.assertEqual(
            len(restaurants_with_distance),
            len(available_restaurants),
        )
        self.assertIn(available_restaurants[0], restaurants_with_distance)

    @patch('restaurateur.views.get_coordinates')
    def test_get_coordinates(self, mock_get_coordinates):
        get_coordinates = mock_get_coordinates()
        get_coordinates.return_value = ('55.7522', '37.6156')
        coordinates = get_coordinates(self.possible_restaurant)

        self.assertEqual(len(coordinates), 2)
        self.assertEqual(type(coordinates[0]), str)
        self.assertEqual(type(coordinates[1]), str)

    @patch('restaurateur.views.get_coordinates', return_value=(
        '55.7522',
        '37.6156',
    ))
    def test_view_orders(self, mock_get_coordinates):
        self.client.force_login(User.objects.first())
        orders_url = reverse('restaurateur:view_orders')
        response = self.client.get(orders_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context['order_items']),
            Order.objects.count(),
        )
        for order_item in response.context['order_items']:
            self.assertTrue(hasattr(
                order_item,
                'available_restaurants_with_distance',
            ))
