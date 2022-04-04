from django.db import transaction
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response

from banners.models import Banner
from .models import Order
from .models import OrderItem
from .models import Product
from .serializers import OrderSerializer


def banners_list_api(request):
    banners = Banner.objects.filter(active=True)

    dumped_banners = []
    for banner in banners:
        dumped_banner = {
            'title': banner.title,
            'src': banner.image.url,
            'text': banner.text,
        }
        dumped_banners.append(dumped_banner)

    return JsonResponse(dumped_banners, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST', ])
@renderer_classes((JSONRenderer, BrowsableAPIRenderer, ))
@transaction.atomic
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    order = Order.objects.create(
        firstname=serializer.validated_data["firstname"],
        lastname=serializer.validated_data["lastname"],
        phonenumber=serializer.validated_data["phonenumber"],
        address=serializer.validated_data["address"]
    )

    products_fields = serializer.validated_data['products']
    order_items = [OrderItem(order=order, **fields) for fields in products_fields]

    for order_item in order_items:
        order_item.price = order_item.calculate_actual_price()

    OrderItem.objects.bulk_create(order_items)

    response_serializer = OrderSerializer(order)
    content = response_serializer.data

    return Response(content, status=status.HTTP_201_CREATED)
