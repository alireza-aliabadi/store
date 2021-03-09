import django_filters
from products.models import Product, Category

CATEGORY_LIST = Category.objects.all()


class ProductFilters(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category', lookup_expr='contains')
    brand = django_filters.CharFilter(field_name='brand', lookup_expr='contains')

    class Meta:
        model = Product
        fields = ['category', 'brand']
        widgets = django_filters.ChoiceFilter(choices=CATEGORY_LIST)
