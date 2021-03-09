from django.contrib import admin
from .models import *


# Register your models here.
class ChildInline(admin.TabularInline):
    model = Category
    fields = ('name', 'slug')
    extra = 1
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'details', 'image']
    search_fields = ('name', 'slug')
    inlines = [ChildInline]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'details', 'image']
    search_fields = ('name', 'slug')
    list_filter = ('slug',)


class ProductMetaInline(admin.TabularInline):
    model = ProductMeta
    fields = ("label", "value")
    show_change_link = True


class ImageInline(admin.TabularInline):
    model = Image
    fields = ("image",)
    show_change_link = True

@admin.register(ShopProduct)
class ShopProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'price']
    list_filter = ('product',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('category', 'brand', 'name', 'details', 'image')
    list_filter = ('category', 'brand')
    search_fields = ('name', 'slug')
    inlines = [ProductMetaInline, ImageInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'text', 'rate']
    list_filter = ('product',)
