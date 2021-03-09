from django.urls import path
from .views import CategoryDetail, ProductDetail, like_product, add_comment, ProductList

urlpatterns = [path('category/<slug:pk>', CategoryDetail.as_view(), name="category_detail"),
               path('content/<slug:pk>', ProductDetail.as_view(), name="product_detail"),
               path('like', like_product, name="product_like"),
               path('add-comment', add_comment, name="add_comment"),
               path('search-product', ProductList.as_view(), name="search"),
               # path('filter', category_filter, name='category_filter')
               ]
