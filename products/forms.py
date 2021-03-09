from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django import forms
from .models import Product, ProductMeta, ShopProduct, Category, Brand
from django.forms.formsets import formset_factory

user = get_user_model()

CATEGORY_CHOICE = []
for item in Category.objects.filter(~Q(name='clothes') & ~Q(name='accessory')):
    CATEGORY_CHOICE.append((item.id, item.name))

BRAND_CHOICE = []
for brand in Brand.objects.all():
    BRAND_CHOICE.append((brand.id, brand.name))


class AddProductForm(forms.Form):
    category = forms.ChoiceField(label=_('Category'), choices=CATEGORY_CHOICE, required=True)
    brand = forms.ChoiceField(label=_('Brand'), choices=BRAND_CHOICE, required=True)
    name = forms.CharField(label=_('Name'), max_length=50, required=True)
    slug = forms.SlugField(label=_('Slug'), allow_unicode=True, required=True)
    detail = forms.CharField(label=_('Detail'), max_length=1500, widget=forms.Textarea, empty_value='')
    image = forms.ImageField(label=_('Image'))
    quantity = forms.IntegerField(label=_('Quantity'), min_value=1)
    price = forms.FloatField(label=_('Price'), min_value=0.0)

    def clean_price(self):
        price = self.cleaned_data.get('price', None)
        if int(price) < 0:
            raise ValidationError(_('price most be positive'), code='invalid')
        return price

    # def clean_category(self):
    #     category = self.cleaned_data.get('category', None)
    #     print(category, type(category))
    #     return category
    #
    # def clean_brand(self):
    #     brand = self.cleaned_data.get('brand', None)
    #     print(brand, type(brand))
    #     return brand
    #
    # def clean_image(self):
    #     image = self.cleaned_data.get('image', None)
    #     print(image, type(image))
    #     return image


class AddProductMeta(forms.Form):
    label = forms.CharField(label=_('Label'), required=True)
    value = forms.CharField(label=_('Value'), required=True)

    def clean_label(self):
        label = self.cleaned_data.get('label', None)
        label = label.lower()
        return label

    def clean_value(self):
        value = self.cleaned_data.get('value', None)
        value = value.lower()
        return value


MetaFormSet = formset_factory(AddProductMeta, max_num=10)
