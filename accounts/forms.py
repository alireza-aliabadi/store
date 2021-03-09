from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django import forms

from accounts.models import Address

User = get_user_model()


class UserRegisterForm(forms.Form):
    # class Meta:
    #     model = User
    #     fields = ('first_name', 'last_name', 'email', 'mobile', 'password1', 'password2')
    #     labels = {'first_name': _('FirstName'), 'last_name': _('LastName'), 'email': _('Email'),
    #               'mobile': _('Mobile'), 'password1': _('Password'), 'password2': _('RepeatPassword')}
    first_name = forms.CharField(label=_('FirstName'), widget=forms.TextInput(attrs={'class': 'form-control'}),
                                 required=True)
    last_name = forms.CharField(label=_('LastName'), widget=forms.TextInput(attrs={'class': 'form-control'}),
                                required=True)
    email = forms.EmailField(label=_('Email'), widget=forms.EmailInput(attrs={'class': 'form-control'}),
                             help_text="please enter valid email address", required=True)
    mobile = forms.IntegerField(label=_('Mobile'), widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                help_text="like 09xxxxxxxxx")
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                required=True)
    password2 = forms.CharField(label=_('RepeatPassword'), widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                required=True)

    def clean(self):
        password1 = self.cleaned_data.get('Password', None)
        password2 = self.cleaned_data.get('RepeatedPassword', None)
        if password1 != password2:
            raise ValidationError(_('password doesn\'t match'), code='invalid')

    def clean_password(self):
        password = self.cleaned_data.get('Password', None)
        if len(password) < 8:
            raise ValidationError(_('password is too short'), code='invalid')
        return password


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'mobile']


class UserImage(forms.ModelForm):
    class Meta:
        model = User
        fields = ['image']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['city', 'street', 'zip_code', 'status']
