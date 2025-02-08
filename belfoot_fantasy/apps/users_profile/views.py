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
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, Token

from apps.users.serializers import CustomUserSerializer
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
    #//TODO ПРОТЕСТИРОВАТЬ
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
                credentials = CustomUserLocalCredentials.objects.get(email=email)
                send_mail('Код для восстановления пароля',
                          f'Ваш код для изменения почты - {credentials.data["otp"]}. Не передавайте его никому',
                          "root@bf13.by",
                          [f'{email}'],
                          fail_silently=False, )
                return Response(f'Письмо с кодом отправлено на почту{email}', status=status.HTTP_200_OK)

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
            if otp == user_credentials.otp:
                user.email = new_email
                user_credentials.email = new_email
                user_credentials.otp = str(randint(100000, 999999))
                user.save()
                user_credentials.save()
                return Response('Успешно', status=status.HTTP_200_OK)

            return Response('Неверный код', status=status.HTTP_403_FORBIDDEN)

        return Response('Пользователя не существует', status=status.HTTP_404_NOT_FOUND)


@permission_classes([IsAuthenticated])
class DeleteAccount(APIView):
    def post(self, request):
        credentials_dict = {'local': CustomUserLocalCredentials,
                            'google': CustomUserGoogleCredentials,
                            'telegram': CustomUserTelegramCredentials}

        user_id = request.data['user_id']
        user = CustomUser.objects.get_object_or_false(object_id=user_id)
        auth_provider = request.data['auth_provider']
        if user:
            credentials = credentials_dict[auth_provider].objects.get(id=user.object_id)
            if auth_provider == 'local' or auth_provider == 'google':
                email = credentials.email
                send_mail('Код для восстановления пароля',
                          f'Ваш код для изменения почты - {user.otp}. Не передавайте его никому',
                          "root@bf13.by",
                          [f'{email}'],
                          fail_silently=False, )
                return Response(f'Письмо с кодом отправлено на почту{email}', status=status.HTTP_200_OK)
            elif auth_provider == 'telegram':
                user_id = user.username
                #telegram_bot.send_message(otp=user.otp, username=user_id)
                return Response(f'сообщение с кодом отправлено в ваш телеграм', status=status.HTTP_200_OK)

            return Response('Указан некорректный провайдер аутентификации', status=status.HTTP_400_BAD_REQUEST)

        return Response('Пользователя не существует', status=status.HTTP_404_NOT_FOUND)


@permission_classes([IsAuthenticated])
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
                return Response('Пользователь удалён', status=status.HTTP_200_OK)
            return Response('Указан неверный код', status=status.HTTP_403_FORBIDDEN)

        return Response('Пользователя не существует', status=status.HTTP_404_NOT_FOUND)

