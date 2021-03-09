from django.core.mail import send_mail
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin


# Create your models here.
class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("Email"), unique=True, db_index=True)
    mobile = models.CharField(_("Mobile"), unique=True, max_length=20)
    first_name = models.CharField(_("First_name"), max_length=50, null=True, blank=True)
    last_name = models.CharField(_("Last_name"), max_length=50, null=True, blank=True)
    image = models.ImageField(_("Image"), upload_to="profile/", null=True, blank=True)
    join_date = models.DateTimeField(_("JoinDate"), default=timezone.now)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    @property
    def full_name(self):
        return str(self.first_name) + ' ' + str(self.last_name)

    def __str__(self):
        return self.full_name

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = UserManager()

    def clean(self):
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Notfications(models.Model):
    pass


class Address(models.Model):
    user = models.ForeignKey(User, verbose_name=_("user"), related_name="address", related_query_name="address",
                             on_delete=models.CASCADE)
    city = models.CharField(_("City"), max_length=50)
    street = models.CharField(_("Street"), max_length=50)
    zip_code = models.CharField(_("ZipCode"), max_length=80)
    status = models.BooleanField(_("Active"), default=False)

    @property
    def full_address(self):
        return str(self.city + "-" + self.street + "/ " + "ZIP code: " + self.zip_code)


class Shop(models.Model):
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE, related_name="shop",
                             related_query_name="shop")
    name = models.CharField(_("Name"), max_length=50)
    slug = models.SlugField(_("slug"), db_index=True)
    description = models.CharField(_("Discription"), max_length=400)
    image = models.ImageField(_("Image"), upload_to="shop/")

    def __str__(self):
        return self.name


class Email(models.Model):
    user = models.ForeignKey(User, verbose_name=_("user_email"), on_delete=models.CASCADE,
                             related_name="recieved_email", related_query_name="recieved_email")
    subject = models.CharField(_("subject"), max_length=50)
    body = models.CharField(_("body"), max_length=350)
