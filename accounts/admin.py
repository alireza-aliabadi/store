from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from products.models import Likes
from .models import Address, Shop, Email

User = get_user_model()


class LikeAdmin(admin.TabularInline):
    model = Likes
    fields = ('product',)
    show_change_link = True


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'is_staff']
    change_password_form = AdminPasswordChangeForm
    ordering = ['email']
    readonly_fields = ['full_name']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'mobile', 'image',
                       'password1', 'password2'),
        }),
    )
    fieldsets = (
        (_('authentication data'), {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'mobile', 'image', 'full_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'join_date')}),
    )
    inlines = [LikeAdmin]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['city', 'street', 'zip_code', 'status']
    list_filter = ('city',)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'description', 'image']
    search_fields = ('slug', 'name')
    list_filter = ('slug',)


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'body']
