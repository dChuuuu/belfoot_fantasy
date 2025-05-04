import base64
from base64 import b64decode, b64encode
from io import BytesIO

from PIL import Image
import jwt
from django.http import Http404
from django.shortcuts import render

import hashlib, hmac

import requests
import re
from random import randint


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


from apps.users.serializers import CustomUserSerializer, UserSerializer

from apps.users.models import (CustomUser, CustomUserGoogleCredentials, CustomUserLocalCredentials,
                                               CustomUserTelegramCredentials)


from ..custom_methods import LocalUser
from ..custom_exceptions import CustomUserException400


@permission_classes([IsAuthenticated])
class ProfilePicture(APIView):
    '''Представление для получения аватарки пользователя по id в access-token'''
    def post(self, request):
        # Получение айдишника из access_token для того, чтобы по нему сохранить изображение
        input_data = LocalUser(request=request).input_data_picture()
        access_token = request.headers['Authorization'].lstrip('Bearer')
        picture = input_data.picture
        user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                                        algorithms=['HS256'], options={'verify_signature': False})['user_id']
        user = CustomUser.objects.get_object_or_false(object_id=user_id)
        # Сохранение изображения в БД
        user.picture = picture
        user.save()
        data = {'user_id': user_id,
                'picture': picture}

        return Response(data=data, status=status.HTTP_200_OK)

    def get(self, request):
        # Проверка на полноту запроса
        try:
            access_token = request.headers['Authorization'].lstrip('Bearer')

            user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                                 algorithms=['HS256'], options={'verify_signature': False})['user_id']
        except AttributeError:
            return Response('query user_id в строке запроса не должно быть пустым',
                            status=status.HTTP_400_BAD_REQUEST)
        # Получение изображения на основании query параметра в запросе uri
        user = CustomUser.objects.get_object_or_false(object_id=user_id)
        data = {'user_id': user.object_id,
                'picture': user.picture}

        return Response(data=data)


@permission_classes([IsAuthenticated])
class ChangeUsername(APIView):
    '''Представление для смены имени пользователя по id из access-token'''
    def post(self, request):
        access_token = request.headers['Authorization'].lstrip('Bearer')
        input_data = LocalUser(request=request).input_data_username()
        new_username = input_data.username
        user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                                        algorithms=['HS256'], options={'verify_signature': False})['user_id']
        user = CustomUser.objects.get_object_or_false(object_id=user_id)
        if user:
            try:
                CustomUser.objects.get_object_or_false(username=new_username)
            except:
                user.username = new_username
                user.save()
                data = {'username': user.username}
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                return Response('Имя пользователя уже занято. Попробуйте другое', status=status.HTTP_400_BAD_REQUEST)


        return Response('Пользователя не существует', status=status.HTTP_404_NOT_FOUND)

@permission_classes([IsAuthenticated])
class ChangeEmail(APIView):
    '''Представление для смены почты по id из access-token'''
    def post(self, request):
        access_token = request.headers['Authorization'].lstrip('Bearer')
        user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                             algorithms=['HS256'], options={'verify_signature': False})['user_id']
        user = CustomUser.objects.get_object_or_false(object_id=user_id)

        if user.auth_provider == 'local':
            email = user.email
            send_mail('Код для изменения почты',
                          f'Ваш код для изменения почты - {user.otp}. Не передавайте его никому',
                          "root@bf13.by",
                          [f'{email}'],
                          fail_silently=False, )
            return Response(f'Письмо с кодом отправлено на почту {email}', status=status.HTTP_200_OK)

        return Response('Невозможно совершить для данного auth_provider', status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
class ChangeEmailConfirmation(APIView):
    '''Подтверждение смены почты для юзера'''
    def post(self, request):
        access_token = request.headers['Authorization'].lstrip('Bearer')
        user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                             algorithms=['HS256'], options={'verify_signature': False})['user_id']
        user = CustomUser.objects.get_object_or_false(object_id=user_id)

        try:
            otp = request.data['otp']
            new_email = request.data['new_email']
        except KeyError:
            raise CustomUserException400('Данные otp и new_email в теле запроса пустые')

        try:
            user_credentials = CustomUserLocalCredentials.objects.get(id=user.object_id)
        except ObjectDoesNotExist:
            raise Http404

        if otp == user.otp:
            user.email = new_email
            user_credentials.email = new_email
            user.otp = str(randint(100000, 999999))
            user.save()
            user_credentials.save()
            return Response('Успешно', status=status.HTTP_200_OK)

        return Response('Неверный код', status=status.HTTP_403_FORBIDDEN)




@permission_classes([IsAuthenticated])
class DeleteAccount(APIView):
    '''Представление для удаления аккаунта пользователя'''
    def post(self, request):
        credentials_dict = {'local': CustomUserLocalCredentials,
                            'google': CustomUserGoogleCredentials,
                            'telegram': CustomUserTelegramCredentials}


        access_token = request.headers['Authorization'].lstrip('Bearer')
        user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                             algorithms=['HS256'], options={'verify_signature': False})['user_id']
        user = CustomUser.objects.get_object_or_false(object_id=user_id)
        auth_provider = str(user.auth_provider)



        try:
            credentials = credentials_dict[auth_provider].objects.get(id=user.object_id)
            if auth_provider == 'local':
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


@permission_classes([IsAuthenticated])
class DeleteAccountConfirmation(APIView):
    '''Представление для удаления аккаунта'''
    def post(self, request):
        credentials_dict = {'local': CustomUserLocalCredentials,
                            'google': CustomUserGoogleCredentials,
                            'telegram': CustomUserTelegramCredentials}
        access_token = request.headers['Authorization'].lstrip('Bearer')
        user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                             algorithms=['HS256'], options={'verify_signature': False})['user_id']
        user = CustomUser.objects.get_object_or_false(object_id=user_id)
        auth_provider = str(user.auth_provider)
        otp = request.data["otp"]
        user = CustomUser.objects.get_object_or_false(object_id=user_id)
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





@permission_classes([])
class GetUserInfo(APIView):
    def get(self, request):
        try:
            user_id = request.GET.get('user_id')
        except AttributeError:
            raise CustomUserException400('Значение user_id в query запроса отсутствует')
        user = CustomUser.objects.get_object_or_false(object_id=user_id)
        user_serializer = UserSerializer(user)
        del user_serializer.data['refresh_token']
        return Response(user_serializer.data, status=status.HTTP_200_OK)
