from rest_framework.serializers import ModelSerializer

from .models import Order, OrderItem, Product


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['name']


class OrderItemDataSerializer(ModelSerializer):
    product_data = ProductSerializer(source='product')

    class Meta:
        model = OrderItem
        fields = ['product_data', 'price', 'quantity', ]


class OrderItemSerializer(ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', ]


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(
        many=True,
        allow_empty=False,
        write_only=True,
    )
    items_data = OrderItemDataSerializer(
        many=True,
        source='items',
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'firstname',
            'lastname',
            'phonenumber',
            'address',
            'products',
            'items_data',
        ]
