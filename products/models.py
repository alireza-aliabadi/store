from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


# Create your models here.


class Category(models.Model):
    name = models.CharField(_("name"), max_length=50)
    slug = models.SlugField(_("slug"), db_index=True)
    details = models.CharField(_("detail"), max_length=200)
    image = models.ImageField(_("image"), upload_to="category/", null=True, blank=True)
    parent = models.ForeignKey('self', verbose_name=_("parent"), on_delete=models.SET_NULL, related_name="child",
                               related_query_name="child", null=True, blank=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

    @property
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'pk': self.pk})


class Brand(models.Model):
    name = models.CharField(_("name"), max_length=50)
    slug = models.SlugField(_("slug"), db_index=True)
    details = models.CharField(_("detail"), max_length=200)
    image = models.ImageField(_("image"), upload_to="brand/", null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, verbose_name=_("category"), on_delete=models.PROTECT,
                                 related_name="product", related_query_name="product")
    brand = models.ForeignKey(Brand, verbose_name=_("brand"), on_delete=models.SET_NULL, related_name="product",
                              related_query_name="product", null=True)
    name = models.CharField(_("name"), max_length=50)
    slug = models.SlugField(_("slug"), db_index=True)
    details = models.CharField(_("detail"), max_length=1500)
    image = models.ImageField(_("image"), upload_to="product/main/")

    def __str__(self):
        return self.name

    @property
    def like_count(self):
        likes = self.product_like.filter(product=self, status=True)
        return likes.count()

    @property
    def min_price(self):
        try:
            min_shop = self.product_shop.filter(product=self).order_by('price')[0]
            minprice = min_shop.price
        except:
            minprice = None
        return minprice


class ProductMeta(models.Model):
    product = models.ForeignKey(Product, verbose_name=_("product"), on_delete=models.CASCADE,
                                related_name="product_meta", related_query_name="product_meta")
    label = models.CharField(_("label"), max_length=100)
    value = models.CharField(_("value"), max_length=1000)

    def get_split(self):
        return self.value.split(",")


class Comment(models.Model):
    user = models.ForeignKey("accounts.User", verbose_name=_("user"), on_delete=models.CASCADE,
                             related_name="comment", related_query_name="comment")
    product = models.ForeignKey(Product, verbose_name=_("product"), on_delete=models.CASCADE,
                                related_name="product_comment", related_query_name="product_comment")
    text = models.CharField(_("text"), max_length=1000)
    rate = models.SmallIntegerField(_("rate"), default=0, validators=[
        MaxValueValidator(5), MinValueValidator(0)
    ])

    def __str__(self):
        return self.user.full_name


class ShopProduct(models.Model):
    shop = models.ForeignKey("accounts.Shop", verbose_name=_("shop"), on_delete=models.CASCADE,
                             related_name="product_shop", related_query_name="product_shop")
    product = models.ForeignKey(Product, verbose_name=_("product"), on_delete=models.PROTECT,
                                related_name="product_shop", related_query_name="product_shop")
    price = models.FloatField(_("price"), default=0)
    quantity = models.PositiveSmallIntegerField(_("quantity"), default=0)

    def __str__(self):
        return str(self.product)


class Image(models.Model):
    product = models.ForeignKey(Product, verbose_name=_("product"), on_delete=models.CASCADE,
                                related_name="product_image", related_query_name="product_image", default='')
    image = models.ImageField(_("image"), upload_to="product/")


class Likes(models.Model):
    product = models.ForeignKey(Product, verbose_name=_("product"), on_delete=models.CASCADE,
                                related_name="product_like", related_query_name="product_like")
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE,
                             related_name="liked_products", related_query_name="liked_products")
    status = models.BooleanField(_("status"), default=False)

    class Meta:
        verbose_name = _("like")
        verbose_name_plural = _("likes")

    def __str__(self):
        return str(self.status)
