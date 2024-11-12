from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from rest_framework_simplejwt.views import token_obtain_pair
from rest_framework.views import APIView
from rest_framework import status

from .serializers import CustomUserSerializer

from rest_framework.decorators import authentication_classes, permission_classes
from .models import CustomUser

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication

import re

import jwt

from django.conf import settings


def token_cookie(user):
    '''Функция принимает пользователя как объект, генерирует рефреш-токен и сохраняет его в пользовательскую БД
       После чего создаётся экземпляр запроса, устанавливаются куки и токены возвращаются в куки'''
    refresh = RefreshToken.for_user(user)
    user.refresh_token = refresh
    user.save()
    response = Response(status=status.HTTP_200_OK)
    response.set_cookie(key='access_token', value=f'{refresh.access_token}', max_age=3600, expires=None,
                        path='/', domain=None, secure=False, httponly=True, samesite="Lax")
    response.set_cookie(key='refresh_token', value=f'{refresh}', max_age=604800, expires=None,
                        path='/', domain=None, secure=False, httponly=True, samesite="Lax")

    return response


def auth(request):
    try:
        JWTAuthentication().authenticate(request)
        return Response(data=f'ЗДЕСЬ{JWTAuthentication().authenticate(request)}')
    # Исключение на случай его отсутствия. Сначала проверяем наличие refresh-токена и генерируем новую пару.
    # Если токен невалиден, или отсутствует, редирект на обычную страницу логина //TODO ПРОВЕРКА ВАЛИДНОСТИ КАК? + ФУНКЦИИ
    except:
        try:
            refresh = request.COOKIES['refresh_token']
            refresh_decoded = jwt.decode(refresh, settings.SECRET_KEY, ['HS256'])
            user_id = refresh_decoded['user_id']
            user = CustomUser.objects.get(id=user_id)
            if user.refresh_token == refresh:
                return token_cookie(user)

        except:
            return Response('Необходимо заново пройти аутентификацию')


@authentication_classes([])
@permission_classes([])
class RegisterUser(APIView):
    '''Класс для регистрации пользователей, принимающий только один метод POST'''


    def post(self, request):

        # Проверка корректности ввода данных для валидации
        try:
            username = request.data['username']
            password = request.data['password']
            email = request.data['email']

        except:
            return Response({"Ошибка": "Некорректные либо неполные данные"}, status=status.HTTP_400_BAD_REQUEST)

        data = {"username": username,
                "password": password,
                "email": email}

        serializer = CustomUserSerializer(data=data)

        # Проверка корректности данных для связей в БД, создание записи пользователя в БД и генерация токена
        if serializer.is_valid():
            user = CustomUser.objects.create(username=username, password=password, email=email)
            return token_cookie(user)

        # Улучшение отображения внешнего вида ошибок
        errors_list = serializer.errors.items()
        errors_list_pretty = {}
        for field, case in errors_list:
            errors_list_pretty[field] = re.search(r"('( ?[а-яА-Я]+)+)", case.__str__()).group(1)

        return Response({"Ошибка": f"{errors_list_pretty}"}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([])
@permission_classes([])
class TokenAuthUser(APIView):
    '''Аутентификация пользователя через JWT'''
    def post(self, request):

        # Проверка на наличие и валидность access-токена //TODO ЛОГИКА ДАЛЬШЕ
        try:
            JWTAuthentication().authenticate(request)
            return Response(data=f'ЗДЕСЬ{JWTAuthentication().authenticate(request)}')
        # Исключение на случай его отсутствия. Сначала проверяем наличие refresh-токена и генерируем новую пару.
        # Если токен невалиден, или отсутствует, редирект на обычную страницу логина //TODO ПРОВЕРКА ВАЛИДНОСТИ КАК? + ФУНКЦИИ
        except:
            try:
                refresh = request.COOKIES['refresh_token']
                refresh_decoded = jwt.decode(refresh, settings.SECRET_KEY, ['HS256'])
                user_id = refresh_decoded['user_id']
                user = CustomUser.objects.get(id=user_id)
                if user.refresh_token == refresh:
                    return token_cookie(user)

            except:
                    return Response('Необходимо заново пройти аутентификацию')


@authentication_classes([])
@permission_classes([])
class LoginUser(APIView):
    '''Представление для логина пользователя. Требуется только токен'''
    def post(self, request):
        data = request.data
        serializer = CustomUserSerializer(data=data)
        user = CustomUser.objects.get(username=data['username'])
        if user.password == data['password']:
            return token_cookie(user)


@permission_classes([IsAuthenticated])
class LogoutUser(APIView):
    '''Представление для логаута пользователя. Аутентификация необходима'''
    def post(self, request):
        refresh = request.COOKIES['refresh_token']
        refresh_decoded = jwt.decode(refresh, settings.SECRET_KEY, ['HS256'])
        user_id = refresh_decoded['user_id']
        user = CustomUser.objects.get(id=user_id)
        user.refresh_token = None
        user.save()
        response = Response(status=status.HTTP_200_OK)
        response.set_cookie(key='access_token', value=f'{None}', max_age=3600, expires=None,
                            path='/', domain=None, secure=False, httponly=True, samesite="Lax")
        response.set_cookie(key='refresh_token', value=f'{None}', max_age=604800, expires=None,
                            path='/', domain=None, secure=False, httponly=True, samesite="Lax")

        return response




@permission_classes([IsAuthenticated])
class SecuredView(APIView):
    '''Тестовое представление для проверки прав доступа(авторизации)'''

    def get(self, request):

        return Response('Успешный запрос')