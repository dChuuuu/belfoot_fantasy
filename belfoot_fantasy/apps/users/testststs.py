from rest_framework_simplejwt.views import token_obtain_pair, TokenRefreshView
from django.conf import settings

DJANGO_SETTING_MODULE = settings

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (

        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}


