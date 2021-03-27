from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from foodcartapp.factories import ProductFactory, ProductCategoryFactory
from foodcartapp.models import Order, OrderItem


class RegisterOrderTests(APITestCase):

    def setUp(self):
        ProductCategoryFactory.create_batch(3)
        ProductFactory.create_batch(2)

    def test_register_order(self):
        """Expected correct order saving and answer about user."""
        orders_count_before = Order.objects.count()
        order_items_count_before = OrderItem.objects.count()
        data = {
            'products': [
                {'product': 1, 'quantity': 1},
                {'product': 2, 'quantity': 2}
            ],
            'firstname': 'Ivan',
            'lastname': 'Ivanov',
            'phonenumber': '79138887766',
            'address': 'Москва, Тверская 1'
        }
        url = reverse('foodcartapp:register-order')
        response = self.client.post(url, data, format='json')
        last_order = Order.objects.last()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), orders_count_before + 1)
        self.assertEqual(
            OrderItem.objects.count(),
            order_items_count_before + 2,
        )
        self.assertEqual(last_order.firstname, data['firstname'])
        self.assertEqual(last_order.phonenumber, data['phonenumber'])
        self.assertEqual(
            last_order.items.first().id,
            data['products'][0]['product'],
        )
        self.assertEqual(
            last_order.items.first().quantity,
            data['products'][0]['quantity'],
        )
