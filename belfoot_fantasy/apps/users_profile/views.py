import base64
from base64 import b64decode, b64encode
from io import BytesIO

from PIL import Image
import jwt
from django.shortcuts import render

import hashlib, hmac

import requests
import re
from random import randint

from django.contrib.auth import authenticate, login
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, Token
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.users.serializers import CustomUserSerializer, UserSerializer
# from apps.users.models import CustomUser, CustomUserGoogleCredentials, \
#     CustomUserLocalCredentials, CustomUserTelegramCredentials
from apps.users.models import (CustomUser, CustomUserGoogleCredentials, CustomUserLocalCredentials,
                                               CustomUserTelegramCredentials)
#from apps.users.telegram_auth import main as telegram_bot
from rest_framework_simplejwt.models import TokenUser

@permission_classes([IsAuthenticated])
class ProfilePicture(APIView):
    def post(self, request):

        access_token = request.headers['Authorization'].lstrip('Bearer')
        picture = request.data['picture']
        user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                                        algorithms=['HS256'], options={'verify_signature': False})['user_id']

        user = CustomUser.objects.get_object_or_false(object_id=user_id)
        if user:
            user.picture = picture
            user.save()
            data = {'user_id': user_id,
                    'picture': picture}
            return Response(data=data, status=status.HTTP_200_OK)

        return Response('Пользователя не существует', status=status.HTTP_404_NOT_FOUND)

    def get(self, request):
        user_id = request.GET.get('user_id')
        user = CustomUser.objects.get_object_or_false(object_id=user_id)

        if user:
            data = {'user_id': user.object_id,
                    'picture': user.picture}
            return Response(data=data)
        return Response('Пользователя не существует', status=status.HTTP_404_NOT_FOUND)

@permission_classes([IsAuthenticated])
class ChangeUsername(APIView):
    def post(self, request):
        access_token = request.headers['Authorization'].lstrip('Bearer')
        new_username = request.data['username']
        user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                                        algorithms=['HS256'], options={'verify_signature': False})['user_id']
        user = CustomUser.objects.get_object_or_false(object_id=user_id)
        if user:
            username_check = CustomUser.objects.get_object_or_false(username=new_username)
            if username_check:
                return Response('Имя пользователя уже занято. Попробуйте другое', status=status.HTTP_200_OK)

            user.username = new_username
            user.save()
            data = {'username': user.username}
            return Response(data=data, status=status.HTTP_200_OK)

        return Response('Пользователя не существует', status=status.HTTP_404_NOT_FOUND)

@permission_classes([IsAuthenticated])
class ChangeEmail(APIView):
    def post(self, request):
        access_token = request.headers['Authorization'].lstrip('Bearer')
        user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                             algorithms=['HS256'], options={'verify_signature': False})['user_id']
        user = CustomUser.objects.get_object_or_false(object_id=user_id)
        if user:
            if user.auth_provider == 'local':
                email = user.email

                send_mail('Код для изменения почты',
                          f'Ваш код для изменения почты - {user.otp}. Не передавайте его никому',
                          "root@bf13.by",
                          [f'{email}'],
                          fail_silently=False, )
                return Response(f'Письмо с кодом отправлено на почту {email}', status=status.HTTP_200_OK)

            return Response('Невозможно совершить для данного auth_provider', status=status.HTTP_400_BAD_REQUEST)

        return Response('Пользователя не существует', status=status.HTTP_404_NOT_FOUND)


@permission_classes([IsAuthenticated])
class ChangeEmailConfirmation(APIView):
    def post(self, request):
        access_token = request.headers['Authorization'].lstrip('Bearer')
        user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                             algorithms=['HS256'], options={'verify_signature': False})['user_id']
        user = CustomUser.objects.get_object_or_false(object_id=user_id)
        otp = request.data['otp']
        new_email = request.data['new_email']
        if user:
            user_credentials = CustomUserLocalCredentials.objects.get(id=user.object_id)
            if otp == user.otp:
                user.email = new_email
                user_credentials.email = new_email
                user.otp = str(randint(100000, 999999))
                user.save()
                user_credentials.save()
                return Response('Успешно', status=status.HTTP_200_OK)

            return Response('Неверный код', status=status.HTTP_403_FORBIDDEN)

        return Response('Пользователя не существует', status=status.HTTP_404_NOT_FOUND)


@permission_classes([])
class DeleteAccount(APIView):
    def post(self, request):
        credentials_dict = {'local': CustomUserLocalCredentials,
                            'google': CustomUserGoogleCredentials,
                            'telegram': CustomUserTelegramCredentials}

        user_id = request.data['user_id']
        user = CustomUser.objects.get_object_or_false(object_id=user_id)
        auth_provider = request.data['auth_provider']
        if user:
            try:
                credentials = credentials_dict[auth_provider].objects.get(id=user.object_id)
                if auth_provider == 'local':
                    JWTAuthentication(request)
                    email = credentials.email
                    send_mail('Код для удаления аккаунта',
                              f'Ваш код для удаления аккаунта - {user.otp}. Не передавайте его никому',
                              "root@bf13.by",
                              [f'{email}'],
                              fail_silently=False, )
                    return Response(f'Письмо с кодом отправлено на почту {email}', status=status.HTTP_200_OK)

                elif auth_provider == 'telegram':
                    user_id = credentials.user_id
                    token = '7754925216:AAGC16jCqaPOxHMo-jkCI6sPt_PPPWt08Lc'
                    url = f"https://api.telegram.org/bot{token}/sendMessage"
                    payload = {
                        'chat_id': user_id,
                        'text': f'Ваш код для удаления аккаунта - {user.otp}. Не передавайте его никому'
                    }
                    requests.post(url, json=payload)
                    return Response(f'сообщение с кодом отправлено в ваш телеграм', status=status.HTTP_200_OK)


                elif auth_provider == 'google':
                    email = credentials.email
                    send_mail('Код для удаления аккаунта',
                              f'Ваш код для удаления аккаунта - {user.otp}. Не передавайте его никому',
                              "root@bf13.by",
                              [f'{email}'],
                              fail_silently=False, )
                    return Response(f'Письмо с кодом отправлено на почту {email}', status=status.HTTP_200_OK)

                return Response('Указан некорректный провайдер аутентификации', status=status.HTTP_400_BAD_REQUEST)
            except:

                return Response('Отказано в доступе', status=status.HTTP_403_FORBIDDEN)

        return Response('Пользователя не существует', status=status.HTTP_404_NOT_FOUND)


@permission_classes([])
class DeleteAccountConfirmation(APIView):
    def post(self, request):
        credentials_dict = {'local': CustomUserLocalCredentials,
                            'google': CustomUserGoogleCredentials,
                            'telegram': CustomUserTelegramCredentials}
        user_id = request.data['user_id']
        otp = request.data['otp']
        auth_provider = request.data['auth_provider']
        user = CustomUser.objects.get_object_or_false(object_id=user_id)
        if user:
            if otp == user.otp:
                credentials = credentials_dict[auth_provider].objects.get(id=user.object_id)
                user.delete()
                credentials.delete()
                if auth_provider == 'google':
                    access_token = request.data['access_token']
                    url = f"https://oauth2.googleapis.com/revoke?token={access_token}"
                    response = requests.post(url)
                    if response.status_code != 200:
                        return Response('Невозможно удалить пользователя. Неверный токен', status
                            =status.HTTP_403_FORBIDDEN)

                return Response('Пользователь удалён', status=status.HTTP_200_OK)
            return Response('Указан неверный код', status=status.HTTP_403_FORBIDDEN)

        return Response('Пользователя не существует', status=status.HTTP_404_NOT_FOUND)


@permission_classes([])
class GetUserInfo(APIView):

    def get(self, request):
        user_id = request.GET.get('user_id')
        user = CustomUser.objects.get_object_or_false(object_id=user_id)

        if user:
            user_serializer = UserSerializer(user)
            return Response(user_serializer.data, status=status.HTTP_200_OK)

        else:
            return Response('Пользователя не существует либо неверный auth_provider',
                            status=status.HTTP_404_NOT_FOUND)