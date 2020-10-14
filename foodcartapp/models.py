from collections import Counter

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name='категория', related_name='products')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2)
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True)
    description = models.TextField('описание', max_length=500, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='menu_items')
    availability = models.BooleanField('в продаже', default=True, db_index=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]


class Order(models.Model):
    CANCELED = '0'
    UNPROCESSED = '1'
    IN_PROGRESS = '2'
    ON_THE_WAY = '3'
    DELIVERED = '4'
    STATUSES = [
        (CANCELED, 'Отменен'),
        (UNPROCESSED, 'Необработанный'),
        (IN_PROGRESS, 'Выполняется'),
        (ON_THE_WAY, 'В пути'),
        (DELIVERED, 'Доставлен')
    ]

    CASH_TO_COURIER = '0'
    INTERNET_PAYMENT = '1'
    CARD_TO_COURIER = '2'
    PAYMENT_METHODS = [
        (CASH_TO_COURIER, 'Наличными курьеру'),
        (INTERNET_PAYMENT, 'Интернет-оплата'),
        (CARD_TO_COURIER, 'Картой курьеру')
    ]

    firstname = models.CharField('имя', max_length=50)
    lastname = models.CharField('фамилия', max_length=50)
    phonenumber = models.CharField('мобильный номер', max_length=11)
    address = models.CharField('адрес', max_length=100)
    status = models.CharField('статус', max_length=2, choices=STATUSES, default=UNPROCESSED)
    comment = models.TextField('комментарий', blank=True)
    registrated_at = models.DateTimeField('поступил', default=timezone.now)
    called_at = models.DateTimeField('дозвон', blank=True, null=True)
    delivered_at = models.DateTimeField('доставлен', blank=True, null=True)
    payment = models.CharField('способ оплаты', max_length=2, choices=PAYMENT_METHODS, default=CASH_TO_COURIER)
    restaurant = models.ForeignKey(Restaurant, null=True, blank=True,
                                   on_delete=models.SET_NULL, verbose_name='ресторан',  related_name='orders')

    def get_total_price(self):
        return self.items.all().aggregate(Sum('price'))['price__sum']

    def get_admin_change_url(self):
        return reverse('admin:foodcartapp_order_change', args=(self.id,), current_app='foodcartapp')

    def get_available_restaurants(self):
        order_items = self.items.all()
        available_restaurants = []
        available_restaurants_for_each_product_in_order = []

        for order_item in order_items:
            available_restaurants_for_each_product_in_order.append([rmi.restaurant for rmi in RestaurantMenuItem.objects
                                                                   .filter(product=order_item.product)
                                                                   .filter(availability=True)])

        if len(available_restaurants_for_each_product_in_order) == 0:
            return ['Нет доступных ресторанов']

        for available_restaurant in available_restaurants_for_each_product_in_order:
            if len(available_restaurant) == 0:
                return ['Нет доступных ресторанов']

        all_restaurents = []
        [all_restaurents.extend(available_restaurant) for available_restaurant in
         available_restaurants_for_each_product_in_order]

        all_restaurents_with_count = dict(Counter(all_restaurents))

        for restaurant, restaurant_count in all_restaurents_with_count.items():
            if not restaurant_count == len(available_restaurants_for_each_product_in_order):
                continue
            available_restaurants.append(restaurant)

        if len(available_restaurants) == 0:
            return ['Нет доступных ресторанов']

        return available_restaurants

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                verbose_name='Товар', related_name='order_items')
    quantity = models.PositiveSmallIntegerField('количество', validators=[MinValueValidator(1)])
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              verbose_name='Заказ', related_name='items')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2, blank=True)

    def calculate_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} - {self.order}"

    class Meta:
        verbose_name = 'товар заказа'
        verbose_name_plural = 'товары заказа'
