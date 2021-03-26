from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from foodcartapp.factories import ProductFactory, ProductCategoryFactory


class RegisterOrderTests(APITestCase):

    def setUp(self):
        ProductCategoryFactory.create_batch(3)
        ProductFactory.create_batch(2)

    def test_register_order(self):
        self.data = {
            "products": [
                {"product": 1, "quantity": 1},
                {"product": 2, "quantity": 2}
            ],
            "firstname": "Ivan",
            "lastname": "Ivanov",
            "phonenumber": "79138887766",
            "address": "Москва, Тверская 1"
        }
        url = reverse("foodcartapp:register-order")
        response = self.client.post(url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
