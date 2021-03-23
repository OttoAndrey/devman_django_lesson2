from django.db import models
from django.db.models import Sum


class OrderQuerySet(models.QuerySet):
    def get_total_price(self):
        return self.annotate(total_price=Sum('items__price'))


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)
