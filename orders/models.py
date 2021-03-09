from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db import models

from products.models import Product

User = get_user_model()


# Create your models here.
class Order(models.Model):
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE,
                             related_name="order", related_query_name="order")
    description = models.CharField(verbose_name=_("description"), max_length=1500, default="")
    created_at = models.DateTimeField(_("created_date"), auto_now=True)
    updated_at = models.DateTimeField(_("updated_date"), auto_now=True)
    create_time = models.DateTimeField(_("JoinDate"), default=timezone.now)

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")
        ordering = ['-created_at']

    @property
    def price(self):
        return sum([item.total_price for item in self.order_items.all()])

    @property
    def payment_price(self):
        return self.payment.amount

    def __str__(self):
        return self.description


class OrderItems(models.Model):
    order = models.ForeignKey(Order, verbose_name=_("order"), on_delete=models.CASCADE,
                              related_name="order_items", related_query_name="order_items")
    shop_product = models.ForeignKey("products.ShopProduct", verbose_name=_("shop_product"),
                                     on_delete=models.PROTECT)
    product = models.ForeignKey(Product, verbose_name=_("product"), related_name="order_item",
                                related_query_name="order_item", on_delete=models.PROTECT, default="")
    count = models.PositiveSmallIntegerField(_("count"), default=0)
    price = models.PositiveIntegerField(_("price"), default=0)

    class Meta:
        verbose_name = _("orederitem")
        verbose_name_plural = _("orderitems")

    @property
    def total_price(self):
        return self.count * self.price


class Basket(models.Model):
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE,
                             related_name="basket", related_query_name="basket")


class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, verbose_name=_("basket"), on_delete=models.CASCADE,
                               related_name="basket_items", related_query_name="basket_items")
    shop_product = models.ForeignKey("products.ShopProduct", verbose_name=_("shop_product"),
                                     on_delete=models.PROTECT)
    product = models.ForeignKey(Product, verbose_name=_("product"), related_name="basket",
                                related_query_name="basket", on_delete=models.CASCADE, default="")
    quantity = models.IntegerField(verbose_name=_("quantity"), default=1)


class Payment(models.Model):
    order = models.OneToOneField(Order, verbose_name=_("order"), on_delete=models.CASCADE,
                                 related_name="payment", related_query_name="payment")
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE,
                             related_name="payment", related_query_name="payment")
    amount = models.PositiveIntegerField(_("payment"), default=0)
