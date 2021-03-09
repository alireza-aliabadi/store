from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from orders.models import Basket
from .models import SlideShow
from products.models import Category, Product
from django.db.models import Q


# Create your views here.

class MainPage(TemplateView):
    template_name = 'main/index.html'
    extra_context = {'slides': SlideShow.objects.all(),
                     'categories': Category.objects.filter(~Q(parent__name=None)).annotate(id_count=Count('id')).order_by(
                         '-id')[:6],
                     'products': Product.objects.annotate(id_count=Count('id')).order_by('-id')[:6],
                     'cloth': Category.objects.filter(Q(parent__name='clothes')),
                     'accessories': Category.objects.filter(Q(parent__name='accessory'))
                     }

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user = self.request.user
        basket_items = []
        if user.is_authenticated:
            basket = Basket.objects.get(user=user)
            if basket:
                basket_items = basket.basket_items.all()
        else:
            redirect('login')
        context['basket_items'] = basket_items
        products = Product.objects.filter(Q(category__name__contains='clothes') |
                                          Q(category__parent__name__contains='clothes'))
        context['clothes_product'] = products
        accessory_product = Product.objects.filter(Q(category__name__contains='accessory') |
                                                   Q(category__parent__name__contains='accessory'))
        context['accessory_product'] = accessory_product
        return context
