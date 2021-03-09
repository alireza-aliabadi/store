from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.models import Address
from orders.models import Basket, BasketItem, Order, OrderItems, Payment
import json

# Create your views here.
from products.models import ShopProduct, Product, Category


class BasketView(LoginRequiredMixin, View):
    permission_denied_message = 'you should login first'

    def post(self, *args, **kwargs):
        user = self.request.user
        try:
            basket = Basket.objects.get(user=user)
        except Basket.DoesNotExist:
            basket = Basket.objects.create(user=user)
        basket_items_list = basket.basket_items.all()
        print(basket_items_list)
        try:
            shop_id = self.request.POST.get('shop_id')
            shop = ShopProduct.objects.get(id=shop_id)
        except ShopProduct.DoesNotExist:
            return HttpResponse("shop doesn't exist", status=401)
        product_id = self.request.POST.get('product_id')
        product = Product.objects.get(id=product_id)

        try:
            basket_item = BasketItem.objects.get(basket=basket, product=product)
            basket_item.quantity += 1
            basket_item.save()
        except BasketItem.DoesNotExist:
            BasketItem.objects.create(basket=basket, shop_product=shop, product=product)
        size = self.request.POST.get('size')
        color = self.request.POST.get('color')
        print(size)
        total_price = 0
        basket_items = basket.basket_items.all()
        for item in basket_items:
            total_price += item.quantity * item.shop_product.price
        context = {'basket_items': basket_items, 'size': size, 'color': color, 'total_price': total_price,
                   'cloth': Category.objects.filter(Q(parent__name='clothes')),
                   'accessories': Category.objects.filter(Q(parent__name='accessory'))}
        print(context)
        return render(self.request, "main/basket.html", context)

        # ---------------- for ajax method ---------------------
        # data = json.loads(self.request.body)
        # user = self.request.user
        # try:
        #     shop = ShopProduct.objects.get(Q(shop__name=data['shop_name']))
        # except ShopProduct.DoesNotExist:
        #     return HttpResponse("shop doesn't exist", status=401)
        # try:
        #     basket = Basket.objects.get(user=user)
        # except:
        #     basket = Basket.objects.create(user=user)
        # product = Product.objects.get(id=data['product_id'])
        # try:
        #     basket_item = BasketItem.objects.get(product=product)
        #     basket_item.quantity += 1
        #     basket_item.save()
        # except:
        #     BasketItem.objects.create(basket=basket, shop_product=shop, product=product)
        # # context = {'shop_name': data['shop_name'], 'price': int(data['price']), 'product': product,
        # #            'size': data['size'], 'color': data['color'],
        # #            'total_price': int(data['price'])}
        # context = {'basket': basket, 'size': data['size'], 'color': data['color']}
        # return render(self.request, "main/basket.html", context)

    def get(self, *args, **kwargs):
        user = self.request.user
        try:
            basket = Basket.objects.get(user=user)
        except Basket.DoesNotExist:
            HttpResponse("Basket doesn't exist choose you favorite product first")
            return redirect("main")
        total_price = 0
        basket_items = basket.basket_items.all()
        for item in basket_items:
            total_price += item.quantity * item.shop_product.price
        context = {'basket_items': basket_items, 'size': "", 'color': "", 'total_price': total_price,
                   'cloth': Category.objects.filter(Q(parent__name='clothes')),
                   'accessories': Category.objects.filter(Q(parent__name='accessory'))}
        return render(self.request, "main/basket.html", context)


@csrf_exempt
def delete_basket(request):
    data = json.loads(request.body)
    try:
        BasketItem.objects.filter(id=data['basket_id']).delete()
        message = "basket item successfully deleted"
    except:
        message = "couldn't delete basket item"
        return HttpResponse("some error happened", status=500)

    return HttpResponse(json.dumps({'mssg': message}), status=201)


@csrf_exempt
def add_quantity(request):
    data = json.loads(request.body)
    basket_item = BasketItem.objects.get(id=data['item_id'])
    basket_item.quantity = int(data['value'])
    basket_item.save()
    basket = basket_item.basket
    item_total_price = basket_item.quantity * basket_item.shop_product.price
    total_price = 0
    for item in basket.basket_items.all():
        total_price += item.quantity * item.shop_product.price
    response = {'quantity': basket_item.quantity, 'item_total_price': item_total_price, 'total_price': total_price,
                'item_id': basket_item.id}
    return HttpResponse(json.dumps(response), status=201)


class OrderView(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        user = self.request.user
        try:
            basket = Basket.objects.get(user=user)
        except Basket.DoesNotExist:
            HttpResponse("add some product to basket first")
            return redirect("main")
        basket_list = basket.basket_items.all()
        items = basket_list
        total_price = self.request.POST.get('total_price')
        order = Order.objects.create(user=user)
        for item in items:
            order_item = OrderItems.objects.filter(order=order, shop_product=item.shop_product, product=item.product)
            if not order_item:
                OrderItems.objects.create(order=order, shop_product=item.shop_product, product=item.product,
                                          count=item.quantity, price=item.shop_product.price)
            else:
                order_item.update(count=item.quantity, price=item.shop_product.price)
        order_list = order.order_items.all()
        basket.delete()
        address = Address.objects.filter(user=user, status=True)[0]
        context = {'order_list': order_list, 'total_price': total_price, 'address': address.full_address,
                   'order': order, 'cloth': Category.objects.filter(Q(parent__name='clothes')),
                   'accessories': Category.objects.filter(Q(parent__name='accessory'))}
        return render(self.request, "main/order.html", context)

    def get(self, *args, **kwargs):
        user = self.request.user
        try:
            order = Order.objects.get(user=user)
        except Order.DoesNotExist:
            HttpResponse("no order added")
            return redirect("main")
        address = Address.objects.filter(user=user, status=True)[0]
        order_list = order.order_items.all()
        total_price = 0
        for item in order_list:
            total_price += item.price * item.count
        context = {'order_list': order_list, 'total_price': total_price, 'address': address.full_address,
                   'order': order, 'cloth': Category.objects.filter(Q(parent__name='clothes')),
                   'accessories': Category.objects.filter(Q(parent__name='accessory'))}
        return render(self.request, "main/order.html", context)


@csrf_exempt
def add_payment(request):
    user = request.user
    data = json.loads(request.body)
    order = Order.objects.get(id=data['order_id'])
    payment = Payment.objects.filter(order=order, user=user)
    if not payment:
        Payment.objects.create(order=order, user=user, amount=data['amount'])
    else:
        payment.update(amount=data['amount'])
    return HttpResponse(json.dumps({'message': "successful payment"}), status=201)
