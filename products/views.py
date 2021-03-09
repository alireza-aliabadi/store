from braces.views import JSONResponseMixin, AjaxResponseMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
import json
import traceback
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from orders.models import Basket
from products.filters import ProductFilters
from .models import Product, Category, ShopProduct, Likes, Comment, Brand
from django.views.generic.detail import DetailView
from django.views.generic import ListView


# Create your views here.
class CategoryDetail(JSONResponseMixin, AjaxResponseMixin, DetailView):
    model = Category
    slug_field = 'pk'
    slug_url_kwarg = 'pk'
    template_name = 'main/category_detail.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data()
        context['child_categories'] = Category.objects.filter(parent=self.get_object())
        category = self.get_object()
        context['current_category'] = category
        category_tree = []
        print(category)
        print(type(category.parent))
        if category.name:
            print('ok')
        # while category.parent:
        #     category_tree.append(category.parent)
        #     category = category.parent
        # for i in range(3):
        #     if category.parent:
        #         category_tree.append(category.parent)
        #     category = category.parent
        # parent = category_tree.pop(0)
        # context['tree'] = category_tree[::-1]
        context['parent'] = category.parent
        print(category_tree)
        # print(parent)
        products = Product.objects.filter(Q(category=self.get_object()) | Q(category__parent=self.get_object()))
        context['products'] = products
        categories = []
        brands = []
        for product in products:
            categories.append(product.category)
            brands.append(product.brand)
        context['categories'] = set(categories)
        context['brands'] = set(brands)
        context['cloth'] = Category.objects.filter(Q(parent__name='clothes'))
        context['accessories'] = Category.objects.filter(Q(parent__name='accessory'))
        basket_items = []
        if user.is_authenticated:
            basket = Basket.objects.get(user=user)
            if basket:
                basket_items = basket.basket_items.all()
        else:
            redirect('login')
        context['basket_items'] = basket_items
        return context

    def get_ajax(self, request, *args, **kwargs):
        data = json.loads(request.GET.get('data'))
        category = self.get_object()
        products = Product.objects.filter(Q(category=category) | Q(category__parent=category))
        product_list = products
        if data['category']:
            product_list = product_list.filter(Q(category__name__in=data['category']))
        if data['brand']:
            product_list = product_list.filter(Q(brand__name__in=data['brand']))
        if data['less_val'] and data['max_val']:
            less_val = float(data['less_val'])
            max_val = float(data['max_val'])
            product_price_list = [x.min_price for x in product_list if x.min_price]
            shops = ShopProduct.objects.filter(Q(price__in=product_price_list), price__gte=less_val, price__lte=max_val)
            product_list = Product.objects.filter(Q(product_shop__in=shops))
        if data['order']:
            product_list = product_list.order_by('-id')
        if data['price_a']:
            product_list = sorted(product_list, key=lambda x: x.min_price)
        if data['price_d']:
            product_list = sorted(product_list, key=lambda x: x.min_price, reverse=True)
        items = []
        for item in product_list:
            try:
                min_shop = ShopProduct.objects.filter(product=item).order_by('price')[0]
                items.append({
                    'id': item.pk,
                    'name': item.name,
                    'image': item.image.url,
                    'price': min_shop.price
                })
            except:
                items.append({
                    'id': item.pk,
                    'name': item.name,
                    'image': item.image.url,
                    'price': None
                })
        response = {'products': items}
        return HttpResponse(json.dumps(response), status=201)


class ProductDetail(DetailView):
    model = Product
    slug_field = 'pk'
    slug_url_kwarg = 'pk'
    template_name = 'main/product-content.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data()
        product = self.get_object()
        context['product'] = product
        category = self.get_object().category
        context['category'] = category
        related_products = Product.objects.filter(category=category).annotate(id_count=Count('id')).order_by('-id')[:4]
        context['related_product'] = related_products
        context['first_related'] = context['related_product'][0]
        context['cloth'] = Category.objects.filter(Q(parent__name='clothes'))
        context['accessories'] = Category.objects.filter(Q(parent__name='accessory'))
        try:
            shop = ShopProduct.objects.filter(product=self.get_object())
            context['min_shop'] = \
                shop.order_by('price')[0]
            context['shops'] = shop
        except:
            print(traceback.format_exc())
            context['min_shop'] = None
            context['shops'] = None
        context['meta'] = self.get_object().product_meta.all()
        context['comments'] = self.get_object().product_comment.all()
        basket_items = []
        if user.is_authenticated:
            basket = Basket.objects.get(user=user)
            if basket:
                basket_items = basket.basket_items.all()
        else:
            redirect('login')
        context['basket_items'] = basket_items
        gallery = product.product_image.all()
        context['gallery'] = gallery
        return context


@login_required
@csrf_exempt
def like_product(request):
    data = json.loads(request.body)
    user = request.user
    try:
        product = Product.objects.get(id=data['productid'])
    except Product.DoesNotExist:
        return HttpResponse('product doesn\'t exist', status=404)
    try:
        product_like = Likes.objects.get(user=user, product=product)
        product_like.status = data['status']
        product_like.save()
    except Likes.DoesNotExist:
        Likes.objects.create(user=user, product=product, status=data['status'])
    response = {'like_counter': product.like_count}
    return HttpResponse(json.dumps(response), status=201)


@login_required
@csrf_exempt
def add_comment(request):
    user = request.user
    data = json.loads(request.body)
    try:
        product = Product.objects.get(id=data['product_id'])
    except Product.DoesNotExist:
        return HttpResponse("that product doesn't exist", status=404)
    try:
        comment = Comment.objects.create(user=user, product=product, text=data['content'], rate=data['rate'])
    except Comment.DoesNotExist:
        return HttpResponse("couldn't create comment", status=500)
    response = {'comment_user': comment.user.full_name, 'comment_text': comment.text, 'comment_rate': comment.rate}
    return HttpResponse(json.dumps(response), status=201)


class ProductList(AjaxResponseMixin, JSONResponseMixin, ListView):
    model = Product
    template_name = "main/product_list.html"
    paginate_by = 4
    paginate_orphans = 30

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super().get_context_data()
    #     shops = []
    #     for product in self.get_queryset():
    #         try:
    #             minshop = ShopProduct.objects.filter(product=product).order_by('price')[0]
    #         except:
    #             minshop = None
    #         shops.append(minshop)
    #     context['filter'] = ProductFilters(self.request.GET, queryset=self.get_queryset())
    #     context['shops'] = shops
    #     context['products'] = self.get_queryset()
    #     context['cloth'] = Category.objects.filter(Q(parent__name='clothes'))
    #     context['accessories'] = Category.objects.filter(Q(parent__name='accessory'))
    #     context['brands'] = Brand.objects.all()
    #     return context
    def get_queryset(self):
        products = super().get_queryset()
        search = self.request.GET.get('q')
        print(search)
        if search:
            print("inside if")
            products = products.filter(Q(name__contains=search) | Q(category__name__contains=search) |
                                       Q(category__parent__name__contains=search) | Q(brand__name__contains=search))
        print(products)
        category_filter = self.request.GET.get('categoryfilter')
        print(type(category_filter))
        print(category_filter)
        if category_filter:
            products = products.filter(category__name=category_filter)
        brandfilter = self.request.GET.get('brandfilter')
        if brandfilter:
            products = products.filter(brand__name=brandfilter)
        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        user = self.request.user
        products = self.get_queryset()
        if self.request.GET.get('latest'):
            products = products.order_by('-id')
        shops = []
        context = super().get_context_data()
        for product in products:
            try:
                minshop = ShopProduct.objects.filter(product=product).order_by('price')[0]
            except:
                minshop = None
            shops.append(minshop)
        context['shops'] = shops
        context['products'] = products
        context['cloth'] = Category.objects.filter(Q(parent__name='clothes'))
        context['accessories'] = Category.objects.filter(Q(parent__name='accessory'))
        context['brands'] = Brand.objects.all()
        basket_items = []
        if user.is_authenticated:
            basket = Basket.objects.get(user=user)
            if basket:
                basket_items = basket.basket_items.all()
        else:
            redirect('login')
        context['basket_items'] = basket_items
        return context

    def get_ajax(self, request, *args, **kwargs):
        data = json.loads(request.GET.get('data'))
        product_list = self.get_queryset()
        if data['less_val'] and data['max_val']:
            less_val = float(data['less_val'])
            max_val = float(data['max_val'])
            # print('less val: ', less_val)
            # print('max val: ', max_val)
            # prices = [x.min_price for x in product_list]
            # print(prices)
            prices2 = [x.min_price for x in product_list if x.min_price]
            # product_list2 = [x for x in product_list if x.min_price]
            # result2 = list(filter(lambda s: less_val <= s <= max_val, prices2))
            # print('result2: ', result2)
            # print(prices2)
            # print('2:', product_list2)
            shops = ShopProduct.objects.filter(Q(price__in=prices2), price__gte=less_val, price__lte=max_val)
            print('shops', shops)
            product_list = Product.objects.filter(Q(product_shop__in=shops))
            # product_list = [a for a in product_list2 if less_val <= a.min_price <= max_val]
            print('result:', product_list)
            if data['price_a']:
                product_list = sorted(product_list, key=lambda x: x.min_price)
            if data['price_d']:
                product_list = sorted(product_list, key=lambda x: x.min_price, reverse=True)
            items = []
            for item in product_list:
                try:
                    min_shop = ShopProduct.objects.filter(product=item).order_by('price')[0]
                    items.append({
                        'id': item.pk,
                        'name': item.name,
                        'image': item.image.url,
                        'price': min_shop.price
                    })
                except:
                    items.append({
                        'id': item.pk,
                        'name': item.name,
                        'image': item.image.url,
                        'price': None
                    })
            response = {'products': items}
            return HttpResponse(json.dumps(response), status=201)
    # def get_ajax(self, request, *args, **kwargs):
    #     data = json.loads(self.request.body)
    #     products = self.get_queryset()
    #     if data['status'] == "True":
    #         products = products.order_by('-id')
    #     context = self.get_context_data()
    #     context['products'] = products
    #     return HttpResponse(request, json.dumps(context), status=200)
# def category_filter(request):
#     data = json.loads(request.body)
#     return
