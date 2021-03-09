from django.contrib import admin
from .models import *
# Register your models here.


class OrderItemInline(admin.TabularInline):
    model = OrderItems
    fields = ('shop_product', 'count', 'price')
    show_change_link = True
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'description', 'price', 'created_at', 'updated_at']
    list_filter = ('created_at', 'updated_at')
    inlines = [OrderItemInline]


class BasketItemInline(admin.TabularInline):
    model = BasketItem
    fields = ('shop_product',)
    extra = 1
    show_change_link = True


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ['user']
    inlines = [BasketItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'order', 'amount']