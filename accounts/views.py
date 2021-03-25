from urllib import parse
from braces.views import JSONResponseMixin, AjaxResponseMixin
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core import serializers
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import UpdateView, BaseFormView
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect as django_redirect
from django.views.generic import FormView
from typing import final
from orders.models import Order, Basket
from products.forms import AddProductForm
from products.models import Category, Product, ShopProduct, Likes, Brand
from .forms import UserRegisterForm, UserForm, UserImage, AddressForm
from .models import Address, Shop

User = get_user_model()


# Create your views here.

class RegisterView(FormView):
    form_class = UserRegisterForm
    template_name = "main/registration/register.html"
    success_url = 'login'
    extra_context = {'cloth': Category.objects.filter(Q(parent__name='clothes')),
                     'accessories': Category.objects.filter(Q(parent__name='accessory'))}

    def post(self, request, *args, **kwargs):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            mobile = form.cleaned_data['mobile']
            User.objects.create_user(first_name=first_name, last_name=last_name, email=email, mobile=mobile,
                                     password=password)
            return redirect('login')
        context = {'form': form}
        return render(request, 'main/registration/register.html', context)

    def get(self, request, *args, **kwargs):
        form = UserRegisterForm()
        context = {'form': form}
        return render(request, 'main/registration/register.html', context)


class UserLoginView(LoginView):
    template_name = 'main/registration/login.html'
    success_url = 'main'
    extra_context = {'cloth': Category.objects.filter(Q(parent__name='clothes')),
                     'accessories': Category.objects.filter(Q(parent__name='accessory'))}

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(request, username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return redirect('main')
        return render(request, 'main/registration/login.html', context={})


class UserLogOut(LogoutView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('main')


class Profile(LoginRequiredMixin, UpdateView):
    model = User
    login_url = 'login'
    permission_denied_message = 'please login first'
    template_name = 'main/profile.html'
    form_class = UserForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user = self.get_object()
        context['user'] = user
        if user.is_staff:
            shop = Shop.objects.get(user=user)
            context['shop_name'] = shop.name
        basket_items = []
        if user.is_authenticated:
            try:
                basket = Basket.objects.get(user=user)
                basket_items = basket.basket_items.all()
            except Basket.DoesNotExist:
                basket_items = None
        else:
            redirect('login')
        context['basket_items'] = basket_items
        context['cloth'] = Category.objects.filter(Q(parent__name='clothes'))
        context['accessories'] = Category.objects.filter(Q(parent__name='accessory'))
        return context

    def form_valid(self, form):
        print(form.cleaned_data['image'])
        if form.is_valid():
            print('form valid')
            form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return str(self.get_object().id)


@csrf_exempt
def change_image(request):
    print("inside func")
    if request.method == "POST":
        user = request.user
        print(request.FILES)
        user.image = request.FILES.get('user_image')
        user.save()
        # user_image = data["user_image"]
        # user.image = user_image
        # print(user_image)
        # user.save()
        # response = {'image': user.image.url}
        print('inside if')
        return HttpResponse(json.dumps({"image": user.image.url}), status=201)
    return HttpResponse(json.dumps({"image": "image url"}), status=400)


class AddressDetail(LoginRequiredMixin, FormView):
    permission_denied_message = "login first"
    model = Address
    template_name = 'main/address_detail.html'
    form_class = AddressForm

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data()
        context['cloth'] = Category.objects.filter(Q(parent__name='clothes'))
        context['accessories'] = Category.objects.filter(Q(parent__name='accessory'))
        # address_id = self.request.GET.get('pk')
        address_id = self.kwargs['pk']
        address = Address.objects.get(id=int(address_id))
        context['address'] = address
        basket_items = []
        if user.is_authenticated:
            try:
                basket = Basket.objects.get(user=user)
                basket_items = basket.basket_items.all()
            except Basket.DoesNotExist:
                basket_items = None
        else:
            redirect('login')
        context['basket_items'] = basket_items
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = AddressForm(request.POST)
        address = context['address']
        print(address)
        if form.is_valid():
            # form.instance = addressf
            # form.save()
            print('inside update')
            address.city = form.cleaned_data['city']
            address.street = form.cleaned_data['street']
            address.zip_code = form.cleaned_data['zip_code']
            if request.POST.get('checkbox') == 'true':
                address.status = True
            elif request.POST.get('checkbox') == 'false':
                address.status = False
            else:
                pass
            print(address.status)
            address.save()
            return redirect('address')
        context['form'] = form
        return render(request, "main/address_detail.html", context)


class AddressUpdate(LoginRequiredMixin, FormView):
    permission_denied_message = "login first"
    model = Address
    template_name = "main/address_list.html"
    form_class = AddressForm

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data()
        context['cloth'] = Category.objects.filter(Q(parent__name='clothes'))
        context['accessories'] = Category.objects.filter(Q(parent__name='accessory'))
        basket_items = []
        if user.is_authenticated:
            try:
                basket = Basket.objects.get(user=user)
                basket_items = basket.basket_items.all()
            except Basket.DoesNotExist:
                basket_items = None
        else:
            redirect('login')
        context['basket_items'] = basket_items
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        context = self.get_context_data()
        form = AddressForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            street = form.cleaned_data['street']
            zip_code = form.cleaned_data['zip_code']
            Address.objects.create(user=user, city=city, street=street, zip_code=zip_code)
            return redirect('address')
        context['form'] = form
        return render(request, "main/address_list.html", context)

    def get(self, request, *args, **kwargs):
        user = request.user
        context = self.get_context_data()
        context['shop_name'] = Shop.objects.get(user=user).name
        context['addresses'] = Address.objects.filter(user=user)
        return render(request, "main/address_list.html", context)


@login_required
@csrf_exempt
def delete_address(request):
    data = json.loads(request.body)
    address_id = data['address_id']
    print(address_id)
    print(type(address_id))
    Address.objects.get(id=address_id).delete()
    return HttpResponse(json.dumps({'result': "true"}), status=201)


# def price_range(x, less_price, max_price):
#     if less_price <= x.min_price <= max_price:
#         return True
#     else:
#         return False


class UserShopPage(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, ListView):
    model = Shop
    permission_denied_message = "login first"
    template_name = "main/user_shop.html"

    def get_queryset(self):
        # name = self.request.GET.get('shop_name')
        name = self.kwargs['shopname']
        print(name, type(name))
        shop = Shop.objects.get(name=name)
        return shop

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        user = self.request.user
        shop = self.get_queryset()
        if shop.user == user:
            context['add_status'] = True
        context['shop'] = shop
        products = Product.objects.filter(Q(product_shop__shop=shop))
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
            try:
                basket = Basket.objects.get(user=user)
                basket_items = basket.basket_items.all()
            except Basket.DoesNotExist:
                basket_items = None
        else:
            redirect('login')
        context['basket_items'] = basket_items
        return context

    def get_ajax(self, request, *args, **kwargs):
        data = json.loads(request.GET.get('data'))
        name = self.kwargs['shopname']
        shop = Shop.objects.get(name=name)
        products = Product.objects.filter(Q(product_shop__shop=shop))
        min_shops = []
        print(products)
        product_list = products
        print('product list', product_list)
        print('recieved data', data, type(data))
        # product_list = serializers.serialize('json', product_list)
        # print(data['category'], type(data['category']))
        # print(data['brand'], type(data['brand']))
        if data['category']:
            product_list = product_list.filter(Q(category__name__in=data['category']))
        if data['brand']:
            product_list = product_list.filter(Q(brand__name__in=data['brand']))
        print(data['less_val'], type(data['less_val']))
        print(data['max_val'], type(data['max_val']))
        if data['less_val'] and data['max_val']:
            print('inside of price if')
            less_val = float(data['less_val'])
            print(less_val, type(less_val))
            max_val = float(data['max_val'])
            print(max_val, type(max_val))
            print('product list before:', product_list, type(product_list))
            # result = []
            # for item in product_list:
            #     print(item.min_price, type(item.min_price))
            #     if less_val <= item.min_price and item.min_price <= max_val:
            #         print('inside if')
            #         result.append(item.id)
            # # product_list = list(filter(lambda x: less_val <= x.min_price <= max_val, product_list))
            # print(result)
            product_price_list = [x.min_price for x in product_list if x.min_price]
            # product_price_list = filter(lambda i: less_val <= int(i) and int(i) <= max_val, product_price_list)
            # # product_list = list(filter(lambda x: x.min_price in product_price_list), product_list)
            # min_price_list = []
            # for x in product_list:
            #     min_shop = x.product_shop.filter(product=x).order_by('price')[0]
            #     minprice = min_shop.price
            #     if less_val <= minprice <= max_val:
            #         min_price_list.append(x)
            # print(min_price_list)
            # print('product price list', list(product_price_list))
            # shops = ShopProduct.objects.filter(Q(shop=shop) & Q(price__range=(less_val, max_val)))
            # shops = ShopProduct.objects.filter(Q(shop=shop) & Q(price__gte=less_val) & Q(price__lte=max_val))
            # print('shops', shops)
            # product_list = Product.objects.filter(Q(product_shop__in=shops))
            shops = ShopProduct.objects.filter(Q(price__in=product_price_list), price__gte=less_val, price__lte=max_val)
            print('shops', shops)
            product_list = Product.objects.filter(Q(product_shop__in=shops))
            print('product list after:', product_list)
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


class Interests(LoginRequiredMixin, ListView):
    model = Product
    permission_denied_message = "please login first"
    template_name = "main/interests.html"
    paginate_by = 12
    paginate_orphans = 30

    def get_queryset(self):
        user = self.request.user
        products = Product.objects.filter(Q(product_like__user=user, product_like__status=True))
        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        user = self.request.user
        context = super().get_context_data()
        context['products'] = self.get_queryset()
        context['user'] = self.request.user
        try:
            shop = Shop.objects.get(user=user)
            context['shop_name'] = shop.name
        except:
            pass
        context['cloth'] = Category.objects.filter(Q(parent__name='clothes'))
        context['accessories'] = Category.objects.filter(Q(parent__name='accessory'))
        basket_items = []
        if user.is_authenticated:
            try:
                basket = Basket.objects.get(user=user)
                basket_items = basket.basket_items.all()
            except Basket.DoesNotExist:
                basket_items = None
        else:
            redirect('login')
        context['basket_items'] = basket_items
        return context


@csrf_exempt
def delete_interest(request):
    data = json.loads(request.body)
    product = Product.objects.get(id=data['product_id'])
    user = request.user
    try:
        Likes.objects.filter(product=product, user=user).delete()
        message = "successfully removed from interests"
    except:
        message = "couldn't found interested product"
        return HttpResponse("some error happened", status=500)

    return HttpResponse(json.dumps({'mssg': message}), status=201)


class UserOrders(LoginRequiredMixin, ListView):
    model = Order
    permission_denied_message = "please login first"
    template_name = "main/user-orders.html"
    paginate_by = 12
    paginate_orphans = 30

    def get_queryset(self):
        user = self.request.user
        order = Order.objects.filter(user=user)
        return order

    def get_context_data(self, *, object_list=None, **kwargs):
        user = self.request.user
        context = super().get_context_data()
        context['orders'] = self.get_queryset()
        context['user'] = self.request.user
        try:
            shop = Shop.objects.get(user=user)
            context['shop_name'] = shop.name
        except:
            pass
        context['cloth'] = Category.objects.filter(Q(parent__name='clothes'))
        context['accessories'] = Category.objects.filter(Q(parent__name='accessory'))
        basket_items = []
        if user.is_authenticated:
            try:
                basket = Basket.objects.get(user=user)
                basket_items = basket.basket_items.all()
            except Basket.DoesNotExist:
                basket_items = None
        else:
            redirect('login')
        context['basket_items'] = basket_items
        return context


def redirect(url, *args, params=None, **kwargs):
    query_params = ""
    if params:
        query_params += '?' + parse.urlencode(params)
    return django_redirect(url + query_params, *args, **kwargs)


class AddProduct(FormView):
    def post(self, request, *args, **kwargs):
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.cleaned_data['category']
            brand = form.cleaned_data['brand']
            name = form.cleaned_data['name']
            slug = form.cleaned_data['slug']
            detail = form.cleaned_data['detail']
            image = form.cleaned_data['image']
            quantity = form.cleaned_data['quantity']
            price = form.cleaned_data['price']
            brand_item = Brand.objects.get(id=int(brand))
            category_item = Category.objects.get(id=int(category))
            product = Product.objects.create(category=category_item, brand=brand_item, name=name, slug=slug,
                                             image=image, details=detail)
            shop = Shop.objects.get(user=request.user)
            ShopProduct.objects.create(shop=shop, product=product, price=price, quantity=quantity)
            return HttpResponseRedirect(reverse('user_shop_page', kwargs={'shopname': shop.name}))
        context = {'form': form}
        return render(request, "main/shop_addproduct.html", context)

    def get(self, request, *args, **kwargs):
        form = AddProductForm()
        context = {'form': form}
        return render(request, "main/shop_addproduct.html", context)
