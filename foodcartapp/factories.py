import factory.fuzzy

from foodcartapp import models


class ProductCategoryFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('sentence', nb_words=2)

    class Meta:
        model = models.ProductCategory


class RestaurantFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('sentence', nb_words=2)
    address = factory.Faker('address', locale='ru_RU')
    contact_phone = factory.Faker('phone_number', locale='ru_RU')

    class Meta:
        model = models.Restaurant


class RestaurantMenuItemFactory(factory.django.DjangoModelFactory):
    restaurant = factory.Iterator(models.Restaurant.objects.all())
    product = factory.Iterator(models.Product.objects.all())
    availability = factory.fuzzy.FuzzyChoice([True, False])

    class Meta:
        model = models.RestaurantMenuItem


class OrderFactory(factory.django.DjangoModelFactory):
    firstname = factory.Faker('first_name')
    lastname = factory.Faker('last_name')
    phonenumber = factory.Faker('phone_number', locale='ru_RU')
    address = factory.Faker('address', locale='ru_RU')

    class Meta:
        model = models.Order


class ProductFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('sentence', nb_words=3)
    category = factory.Iterator(models.ProductCategory.objects.all())
    price = factory.fuzzy.FuzzyDecimal(150.00, 400.00)
    image = factory.django.ImageField(
        color=factory.fuzzy.FuzzyChoice(['magenta', 'blue', 'green']),
    )
    special_status = factory.fuzzy.FuzzyChoice([True, False])
    description = factory.Faker('text')

    class Meta:
        model = models.Product


class OrderItemFactory(factory.django.DjangoModelFactory):
    product = factory.Iterator(models.Product.objects.all())
    quantity = factory.fuzzy.FuzzyInteger(1, 10)
    order = factory.Iterator(models.Order.objects.all())

    # TODO fix it
    price = 100

    class Meta:
        model = models.OrderItem


class OrderWithProductsFactory(OrderFactory):
    items = factory.RelatedFactoryList(
        factory=OrderItemFactory,
        factory_related_name='order',
        size=2,
    )


class RestaurantMenuItemWithAllAvailabilityProductsFactory(
        factory.django.DjangoModelFactory,
):
    restaurant = factory.Iterator(models.Restaurant.objects.all())
    product = factory.Iterator(models.Product.objects.all())
    availability = True

    class Meta:
        model = models.RestaurantMenuItem


class RestaurantMenuItemWithoutAllAvailabilityProductsFactory(
        factory.django.DjangoModelFactory,
):
    restaurant = factory.Iterator(models.Restaurant.objects.all())
    product = factory.Iterator(models.Product.objects.all())
    availability = False

    class Meta:
        model = models.RestaurantMenuItem


class RestaurantWithAllAvailabilityProductsFactory(RestaurantFactory):
    menu_items = factory.RelatedFactoryList(
        factory=RestaurantMenuItemWithAllAvailabilityProductsFactory,
        factory_related_name='restaurant',
        size=2,
    )


class RestaurantWithoutAllAvailabilityProductsFactory(RestaurantFactory):
    menu_items = factory.RelatedFactoryList(
        factory=RestaurantMenuItemWithoutAllAvailabilityProductsFactory,
        factory_related_name='restaurant',
        size=2,
    )
