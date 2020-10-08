from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order
from .models import OrderItem
from .models import Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
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
            },
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
def register_order(request):
    try:
        request.data["products"]
        request.data["firstname"]
        request.data["lastname"]
        request.data["phonenumber"]
        request.data["address"]
    except KeyError:
        return Response({'error': 'One of the keys is not specified.'}, status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(request.data["products"], list) \
        or not isinstance(request.data["firstname"], str) \
        or not isinstance(request.data["lastname"], str) \
        or not isinstance(request.data["phonenumber"], str) \
        or not isinstance(request.data["address"], str):
        return Response({'error': 'One of the keys has wrong type.'}, status=status.HTTP_400_BAD_REQUEST)

    if len(request.data["products"]) == 0:
        return Response({'error': 'Zero items.'}, status=status.HTTP_400_BAD_REQUEST)

    if request.data["phonenumber"] == ''\
        or request.data["firstname"] == ''\
        or request.data["lastname"] == ''\
        or request.data["phonenumber"] == ''\
        or request.data["address"] == '':
        return Response({'error': 'One of the keys is empty.'}, status=status.HTTP_400_BAD_REQUEST)

    for product in request.data["products"]:
        if not isinstance(product['product'], int):
            return Response({'error': 'Product has wrong type.'}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        firstname=request.data["firstname"],
        lastname=request.data["lastname"],
        phone_number=request.data["phonenumber"],
        address=request.data["address"]
    )

    for product in request.data["products"]:
        OrderItem.objects.create(
            product=Product.objects.get(pk=product['product']),
            quantity=product["quantity"],
            order=order
        )

    return Response(request.data, status=status.HTTP_201_CREATED)
