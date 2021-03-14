from django.urls import path
from .views import RegisterView, UserLoginView, UserLogOut, Profile, change_image, AddressUpdate, delete_address,\
    UserShopPage, Interests, delete_interest, UserOrders, AddProduct, AddressDetail

urlpatterns = [
    path('register', RegisterView.as_view(), name="register"),
    path('login', UserLoginView.as_view(), name="login"),
    path('logout', UserLogOut.as_view(), name="logout"),
    path('profile/<int:pk>', Profile.as_view(), name="profile"),
    path('change-image', change_image, name="change_image"),
    path('address', AddressUpdate.as_view(), name='address'),
    path('address-detail/<int:pk>', AddressDetail.as_view(), name='address_detail'),
    path('delete-address', delete_address, name="delete_address"),
    path('shop-page/<str:shopname>/', UserShopPage.as_view(), name="user_shop_page"),
    path('interests', Interests.as_view(), name="user-interests"),
    path('delete_interest', delete_interest, name="delete_interest"),
    path('user-orders', UserOrders.as_view(), name="user_orders"),
    path('shop-add-product', AddProduct.as_view(), name="shop_add_product")]
