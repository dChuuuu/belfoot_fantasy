from django.contrib import admin
from .models import CustomUser
# Register your models here.
from django.views.decorators.csrf import csrf_exempt

csrf_exempt(admin.site.register(CustomUser))
