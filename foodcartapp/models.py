from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from foodcartapp.querysets import OrderQuerySet, ProductQuerySet


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        verbose_name='цена',
        max_digits=8,
        decimal_places=2,
        validators=(MinValueValidator(0.00),),
    )
    image = models.ImageField(
        'картинка',
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=500,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    CANCELED = 0
    UNPROCESSED = 1
    IN_PROGRESS = 2
    ON_THE_WAY = 3
    DELIVERED = 4
    STATUSES = [
        (CANCELED, 'Отменен'),
        (UNPROCESSED, 'Необработанный'),
        (IN_PROGRESS, 'Выполняется'),
        (ON_THE_WAY, 'В пути'),
        (DELIVERED, 'Доставлен'),
    ]

    CASH_TO_COURIER = 0
    INTERNET_PAYMENT = 1
    CARD_TO_COURIER = 2
    PAYMENT_METHODS = [
        (CASH_TO_COURIER, 'Наличными курьеру'),
        (INTERNET_PAYMENT, 'Интернет-оплата'),
        (CARD_TO_COURIER, 'Картой курьеру'),
    ]

    firstname = models.CharField('имя', max_length=50)
    lastname = models.CharField('фамилия', max_length=50)
    phonenumber = PhoneNumberField('мобильный номер')
    address = models.CharField('адрес', max_length=100)
    status = models.IntegerField('статус', choices=STATUSES, default=UNPROCESSED, db_index=True)
    comment = models.TextField('комментарий', blank=True)
    registrated_at = models.DateTimeField('поступил', default=timezone.now, db_index=True)
    called_at = models.DateTimeField('дозвон', blank=True, null=True, db_index=True)
    delivered_at = models.DateTimeField('доставлен', blank=True, null=True, db_index=True)
    payment = models.IntegerField('способ оплаты', choices=PAYMENT_METHODS, db_index=True)
    restaurant = models.ForeignKey(Restaurant, null=True, blank=True,
                                   on_delete=models.SET_NULL, verbose_name='ресторан',  related_name='orders')

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'

    def get_admin_change_url(self):
        return reverse('admin:foodcartapp_order_change', args=(self.id,), current_app='foodcartapp')


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                verbose_name='Товар', related_name='order_items')
    quantity = models.PositiveSmallIntegerField('количество', validators=[MinValueValidator(1)])
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              verbose_name='Заказ', related_name='items')
    price = models.DecimalField(
        verbose_name='цена',
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        validators=(MinValueValidator(0.00),),
    )

    class Meta:
        verbose_name = 'товар заказа'
        verbose_name_plural = 'товары заказа'

    def __str__(self):
        return f"{self.product.name} - {self.order}"

    def calculate_actual_price(self):
        """Returns actual price of item.

        `self.price` contains historical data
        at the time the object was created.
        """
        return self.product.price * self.quantity
