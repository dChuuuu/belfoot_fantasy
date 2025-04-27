from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.contenttypes import fields
from django.http import Http404

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

from ..game.models import UsersCommands


username_validator = UnicodeUsernameValidator()
class CustomUserManager(BaseUserManager):
    """
    Django требует, чтобы кастомные пользователи определяли свой собственный
    класс Manager. Унаследовавшись от BaseUserManager, мы получаем много того
    же самого кода, который Django использовал для создания User (для демонстрации).
    """

    def create_user(self, username, email, password=None):
        """ Создает и возвращает пользователя с имэйлом, паролем и именем. """
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')
        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """ Создает и возввращет пользователя с привилегиями суперадмина. """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

    def get_object_or_false(self, object_id=None, username=None, email=None):

        if object_id:
            user = CustomUser.objects.get(object_id=object_id)
            return user
        elif username:
            user = CustomUser.objects.get(username=username)
            return user
        elif email:
            user = CustomUser.objects.get(email=email)
            return user
        else:
            raise Http404



class CustomUserLocalCredentials(AbstractUser):
    email = models.EmailField(_("email address"), blank=True, unique=True)

    password = models.CharField(_("password"), max_length=150)
    refresh_token = models.TextField(null=True)
    username = models.CharField(
        _("username"),
        max_length=18,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        }, default=None
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    USERNAME_FIELD = 'username'

    objects = CustomUserManager()


class CustomUserGoogleCredentials(models.Model):
    refresh_token = models.TextField()
    google_refresh_token = models.TextField(default=None, null=True)
    email = models.EmailField(unique=True, default=None)
    objects = CustomUserManager()



class CustomUserTelegramCredentials(models.Model):

    auth_date = models.CharField(default=None)
    hash = models.TextField(default=None)
    first_name = models.CharField(default=None)
    user_id = models.CharField(default=None)
    photo_url = models.TextField(default=None)
    objects = CustomUserManager()


class CustomUser(models.Model):
    '''Модель для обычного пользователя сайта. Наследуется от модели User
       Поля first_name и last_name не используются, поэтому задаётся значение None.
       Поля данных:
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    password = models.CharField(_("password"), max_length=128)'''

    # Отключаем наследуемые поля first_name и last_name из модели AbstractUser
    first_name = None
    last_name = None
    date_joined = None
    is_staff = None
    is_superuser = None
    last_login = None
    password = None
    USERNAME_FIELD = 'username'

    refresh_token = None
    id = models.BigAutoField(primary_key=True, unique=True, default=None)
    # Поля, определяющие имя пользователя и обязательное поле для ввода
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        }, default=None
    )

    auth_provider = models.CharField(max_length=20, choices=[('local', 'Local'), ('google', 'Google'),
                                                            ('telegram', 'Telegram')], default=None)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    email = models.EmailField(unique=True, null=True, blank=True)
    picture = models.TextField(null=True, blank=True)
    otp = models.TextField(null=True, blank=True)
    coins = models.PositiveIntegerField(default=0)
    command = models.ForeignKey(UsersCommands, on_delete=models.CASCADE, null=True, blank=True)
    players = ArrayField(models.CharField(), blank=True, default=list)
    objects = CustomUserManager()
