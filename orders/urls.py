from django.urls import path
from .views import BasketView, delete_basket, OrderView, add_quantity, add_payment
urlpatterns = [
    path('basket', BasketView.as_view(), name="basket"),
    path('delete-basket', delete_basket, name="delete_basket"),
    path('order', OrderView.as_view(), name="order"),
    path('add_quantity', add_quantity, name="add_quantity"),
    path('payment', add_payment, name="payment")]
