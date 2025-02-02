from django.contrib import admin
from .models import CustomUser, CustomUserLocalCredentials, CustomUserGoogleCredentials, CustomUserTelegramCredentials
# Register your models here.
from django.views.decorators.csrf import csrf_exempt

csrf_exempt(admin.site.register(CustomUser))
csrf_exempt(admin.site.register(CustomUserLocalCredentials))
csrf_exempt(admin.site.register(CustomUserGoogleCredentials))
csrf_exempt(admin.site.register(CustomUserTelegramCredentials))