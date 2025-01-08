import json
from random import randint

import requests
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from fake_useragent import UserAgent
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from rest_framework_simplejwt.views import token_obtain_pair
from rest_framework.views import APIView
from rest_framework import status

from .custom_validators import password_validator
from .serializers import CustomUserSerializer

from rest_framework.decorators import authentication_classes, permission_classes
from .models import CustomUser

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication

import re

import jwt

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password

# def token_cookie(user):
#     '''Функция принимает пользователя как объект, генерирует рефреш-токен и сохраняет его в пользовательскую БД
#        После чего создаётся экземпляр запроса, устанавливаются куки и токены возвращаются в куки'''
#
#     refresh = RefreshToken.for_user(user)
#     user.refresh_token = refresh
#     user.save()
#     response = Response(status=status.HTTP_200_OK)
#     response.set_cookie(key='access_token', value=f'{refresh.access_token}', max_age=3600, expires=None,
#                         path='/', domain=None, secure=False, httponly=True, samesite="Lax")
#     response.set_cookie(key='refresh_token', value=f'{refresh}', max_age=604800, expires=None,
#                         path='/', domain=None, secure=False, httponly=True, samesite="Lax")
#
#     return response


@authentication_classes([])
@permission_classes([])
class RegisterUser(APIView):
    '''Класс для регистрации пользователей, принимающий только один метод POST'''

    request_schema_dict = openapi.Schema(
        title=("Регистрация пользователя"),
        type=openapi.TYPE_OBJECT,
        properties={

            'username': openapi.Schema(type=openapi.TYPE_STRING,
                                    description=('Имя пользователя'),
                                    example='test'),

            'password': openapi.Schema(type=openapi.TYPE_STRING,
                                      description=('Пароль пользователя'),
                                      example="123321"),

            'email': openapi.Schema(type=openapi.TYPE_STRING,
                                      description=(
                                          'Почта пользователя'),
                                      example="someuser@example.com"),
        }
    )
    @swagger_auto_schema(request_body=request_schema_dict, responses={200: 'OK'})
    def post(self, request):

        try:
            username = request.data['username']
            password = request.data['password']
            email = request.data['email']
            otp = str(randint(100000, 999999))


        except:
            return Response({"Ошибка": "Некорректные либо неполные данные"}, status=status.HTTP_400_BAD_REQUEST)

        data = {"username": username,
                "password": password,
                "email": email,
                "otp": otp}

        serializer = CustomUserSerializer(data=data)

        # Проверка корректности данных для связей в БД, создание записи пользователя в БД и генерация токена
        if serializer.is_valid():
            if password_validator(password) is None:
                password = make_password(password)
                user = CustomUser.objects.create(username=username, password=password, email=email, otp=otp)
                user.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return password_validator(password)

        # Улучшение отображения внешнего вида ошибок
        errors_list = serializer.errors.items()
        errors_list_pretty = {}
        for field, case in errors_list:
            errors_list_pretty[field] = re.search(r"('( ?[а-яА-Я]+)+)", case.__str__()).group(1)

        return Response({"Ошибка": f"{errors_list_pretty}"}, status=status.HTTP_400_BAD_REQUEST)


# @authentication_classes([])
# @permission_classes([])
# class TokenAuthUser(APIView):
#     '''Аутентификация пользователя через JWT'''
#     request_schema_dict = openapi.Schema(
#         title=("Проверка токена. Обязательно имя пользователя"),
#         type=openapi.TYPE_OBJECT,
#         properties={
#
#             'username': openapi.Schema(type=openapi.TYPE_STRING,
#                                        description=('Имя пользователя'),
#                                        example='test'),}
#     )
#
#     @swagger_auto_schema(request_body=request_schema_dict, responses={200: 'OK'})
#     def post(self, request):
#
#         if banned_user(request):
#             return Response(data={'Статус пользователя': 'Пользователь заблокирован'},
#                             status=status.HTTP_403_FORBIDDEN)
#
#         try:
#                 JWTAuthentication().authenticate(request)
#
#                 return Response(status=status.HTTP_200_OK)
#
#         except:
#             try:
#                 refresh = request.COOKIES['refresh_token']
#                 refresh_decoded = jwt.decode(refresh, settings.SECRET_KEY, ['HS256'])
#                 user_id = refresh_decoded['user_id']
#                 user = CustomUser.objects.get(id=user_id)
#                 if user.refresh_token == refresh:
#                     return token_cookie(user)
#                 else:
#                     return Response(data=request.COOKIES['refresh_token'], status=status.HTTP_403_FORBIDDEN)
#
#             except:
#                     return Response('Необходимо заново пройти аутентификацию', status=status.HTTP_403_FORBIDDEN)


@authentication_classes([])
@permission_classes([])
class LoginUser(APIView):
    '''Обычный логин по паролю. Используется, если отсутствует access-token и refresh-token в куках клиента'''
    request_schema_dict = openapi.Schema(
        title=("Регистрация пользователя"),
        type=openapi.TYPE_OBJECT,
        properties={

            'username': openapi.Schema(type=openapi.TYPE_STRING,
                                       description=('Имя пользователя'),
                                       example='test'),

            'password': openapi.Schema(type=openapi.TYPE_STRING,
                                       description=('Пароль пользователя'),
                                       example="123321"),


        }
    )

    @swagger_auto_schema(request_body=request_schema_dict, responses={200: 'OK'})
    def post(self, request):

        data = request.data
        serializer = CustomUserSerializer(data=data)
        user = authenticate(request=request, username=data['username'], password=data['password'])
        if user is not None:
            login(request, user)
            return Response({"статус": "успешный логин"}, status=status.HTTP_200_OK)
        else:
            return Response({"ошибка": "неверный логин или пароль"}, status=status.HTTP_403_FORBIDDEN)



# @permission_classes([])
# class LogoutUser(APIView):
#     '''Представление для логаута пользователя. Аутентификация необходима'''
#     request_schema_dict = openapi.Schema(
#         title=("Логаут пользователя. Боди пустое, должны быть куки с токенами"),
#         type=openapi.TYPE_OBJECT,
#
#     )
#
#     @swagger_auto_schema(request_body=request_schema_dict, responses={200: 'OK'})
#     def post(self, request):
#         refresh = request.COOKIES['refresh_token']
#         refresh_decoded = jwt.decode(refresh, settings.SECRET_KEY, ['HS256'])
#         user_id = refresh_decoded['user_id']
#         user = CustomUser.objects.get(id=user_id)
#         user.refresh_token = None
#         user.save()
#         response = Response(status=status.HTTP_200_OK)
#         response.set_cookie(key='access_token', value=f'{None}', max_age=3600, expires=None,
#                             path='/', domain=None, secure=False, httponly=True, samesite="Lax")
#         response.set_cookie(key='refresh_token', value=f'{None}', max_age=604800, expires=None,
#                             path='/', domain=None, secure=False, httponly=True, samesite="Lax")
#
#         return response


@permission_classes([IsAuthenticated])
class SecuredView(APIView):
    '''Тестовое представление для проверки прав доступа(авторизации)!!!ДЛЯ БЭКЕНДА'''

    def get(self, request):

        return Response('Успешный запрос')


@authentication_classes([])
@permission_classes([])
class ForgotPassword(APIView):
    '''Представление для получения otp'''
    request_schema_dict = openapi.Schema(
        title=("Получение одноразового кода для сброса пароля на почту юзера. На фронте после этого надо будет делать редирект"
               "на страницу для ввода кода"),
        type=openapi.TYPE_OBJECT,
        properties={

            'email': openapi.Schema(type=openapi.TYPE_STRING,
                                    description=(
                                        'Почта пользователя'),
                                    example="someuser@example.com"),
        }
    )

    @swagger_auto_schema(request_body=request_schema_dict, responses={200: 'OK'})
    def post(self, request):
        email = request.data['email']
        email_instance = CustomUser.objects.get(email=email)
        serializer = CustomUserSerializer(instance=email_instance)
        send_mail('Код для восстановления пароля',
        f'Ваш код для восстановления пароля - {serializer.data["otp"]}. Не передавайте его никому',
    "root@bf13.by",
    [f'{email}'],
        fail_silently=False,)

        #otp = str(randint(100000, 999999))
        #email_instance.otp = otp
        #email_instance.save()
        #if serializer.is_valid(raise_exception=True):
            #serializer.save()
        return Response(data=email_instance.otp)


@authentication_classes([])
@permission_classes([])
class ResetPassword(APIView):
    '''Представление для сброса пароля и генерации нового otp'''

    request_schema_dict = openapi.Schema(
        title=("Ввод кода для смены пароля + смена пароля"),
        type=openapi.TYPE_OBJECT,
        properties={

            'otp': openapi.Schema(type=openapi.TYPE_STRING,
                                       description=('Одноразовый пароль'),
                                       example='test'),

            'new_password': openapi.Schema(type=openapi.TYPE_STRING,
                                       description=('Новый пароль пользователя'),
                                       example="12332321"),

            'email': openapi.Schema(type=openapi.TYPE_STRING,
                                    description=(
                                        'Почта пользователя'),
                                    example="someuser@example.com"),
        }
    )

    @swagger_auto_schema(request_body=request_schema_dict, responses={200: 'OK'})
    def post(self, request):

        otp = request.data['otp']
        email = request.data['email']
        new_password = request.data['new_password']

        try:
            email_instance = CustomUser.objects.get(email=email)

        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if otp == email_instance.otp:
            email_instance.password = new_password
            email_instance.otp = str(randint(100000, 999999))
            email_instance.save()

            return Response(data=f'{email_instance.password}', status=status.HTTP_200_OK)

        return Response(status=status.HTTP_403_FORBIDDEN)


class OAuth2(APIView):

    def post(self, request):
        google_auth_url = 'https://accounts.google.com/o/oauth2/v2/auth'
        client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        redirect_uri = 'https://bf13.by/users/auth/google-oauth2/complete'
        response_type = 'code'
        scope = 'email'
        access_type = 'offline'


class OAuth2Complete(APIView):

    def get(self, request):
        #http://localhost:8000/users/auth/google-oauth2/complete/?code=4%2F0AanRRruy1RTB5e1E2Zsw2_OGGyGveA6lBhkru0tyYU

        google_auth_token_uri = 'https://oauth2.googleapis.com/token'
        client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        client_secret = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
        code = request.GET.get('code')
        grant_type = 'authorization_code'

        #scope = request.GET.get('scope')
        #authuser = request.GET.get('authuser')
        prompt = request.GET.get('prompt')
        redirect_uri = reverse('test_secured_view')

        data = {'code': code,
                #'scope': scope,
                #'authuser': authuser,
                'prompt': prompt,
                'client_secret': client_secret,
                'client_id': client_id,
                'grant_type': grant_type,
                'redirect_uri': redirect_uri}
        ua = UserAgent()

        token_response = requests.post(url=google_auth_token_uri, data=data)
        return Response(token_response)



# class BanUser(APIView):
#     '''Представление для блокировки пользователей'''
#     request_schema_dict = openapi.Schema(
#         title=("Бан пользователя по юзернейму"),
#         type=openapi.TYPE_OBJECT,
#         properties={
#
#             'username': openapi.Schema(type=openapi.TYPE_STRING,
#                                   description=('Имя пользователя'),
#                                   example='test')
#
#         }
#     )
#     def post(self, request):
#
#         try:
#             username = request.data['username']
#             user = CustomUser.objects.get(username=username)
#             user.refresh_token = None
#             user.banned = True
#             user.save()
#
#             return Response(status=status.HTTP_200_OK)
#
#         except:
#             return Response(status=status.HTTP_404_NOT_FOUND)