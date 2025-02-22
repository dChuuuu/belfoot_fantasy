import base64
import hashlib, hmac

import requests

from random import randint

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .custom_validators import password_validator
from .serializers import CustomUserSerializer, UserSerializer
from .models import CustomUser, CustomUserGoogleCredentials, \
    CustomUserLocalCredentials, CustomUserTelegramCredentials

from .custom_exceptions import CustomUserException400

def username_generator(username, username_check):
    # генератор никнеймов в случае дубликата в основной БД с базовой аутентификацией
    counter = 0
    while username == username_check:
        username += str(counter)
        try:
            username_check = CustomUser.objects.get(username=username)
        except:
            pass
    return username


def create_social_user(token_response, email, username, access_token):
    # создание социального аккаунта

    refresh_token = token_response['refresh_token']
    credentials = CustomUserGoogleCredentials.objects.create(email=email, refresh_token=refresh_token)
    try:
        CustomUser.objects.get(username=username)
        username = username + str(randint(0, 99999))
        user = CustomUser.objects.create(username=username, auth_provider='google',
                                         object_id=credentials.id,
                                         email=email,
                                         content_type=ContentType.objects.get_for_model(
                                             CustomUserGoogleCredentials),
                                         otp=str(randint(100000, 999999))
                                         )
        data = {'username': user.username,
                'email': user.email,
                'refresh_token': credentials.refresh_token,
                'access_token': access_token,
                'user_id': user.object_id}

    except:
        user = CustomUser.objects.create(username=username, auth_provider='google',
                                         object_id=credentials.id,
                                         email=email,
                                         content_type=ContentType.objects.get_for_model(
                                                         CustomUserGoogleCredentials),
                                         otp=str(randint(100000, 999999))
                                         )
        data = {'username': user.username,
                'email': user.email,
                'refresh_token': credentials.refresh_token,
                'access_token': access_token}
    return data


def get_social_user(username, access_token):
    user = CustomUser.objects.get(username=username)
    credential = CustomUserGoogleCredentials.objects.get(id=user.object_id)
    data = {'username': user.username,
            'email': credential.email,
            'refresh_token': credential.refresh_token,
            'access_token': access_token,
            'user_id': user.object_id}
    return data


def get_google_token(request):
    google_auth_token_uri = 'https://oauth2.googleapis.com/token'
    client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    client_secret = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
    code = request.GET.get('code')
    grant_type = 'authorization_code'
    prompt = request.GET.get('prompt')
    redirect_uri = 'https://bf13.by' + reverse('google_oauth_complete')
    redirect_uri = redirect_uri[0:-1]
    data = {'code': code,
            'prompt': prompt,
            'client_secret': client_secret,
            'client_id': client_id,
            'grant_type': grant_type,
            'redirect_uri': redirect_uri}
    token_response = requests.post(url=google_auth_token_uri, data=data).json()
    return token_response


class LocalUser:
    def __init__(self, request=None, password=None, username=None, email=None):
        self.request = request
        self.username = username
        self.password = password
        self.email = email

    def __call__(self):
        return self.request

    def input_data_check(self):
        try:
            # Проверка на наличие нужных данных в теле запроса
            self.username = self.request.data['username']
            self.password = self.request.data['password']
            self.email = self.request.data['email']
            #return {'username': self.username, 'password': self.password, 'email': self.email}
            return self
        except KeyError:
            raise CustomUserException400


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
        # Проверка полноты данных предоставленных в запросе и возврат кредов
        input_data = LocalUser(request=request).input_data_check()
        password = input_data.password
        email = input_data.email
        username = input_data.username

        serializer = CustomUserSerializer(data=request.data)

        # Проверка корректности данных для связей в БД, создание записи пользователя в БД и генерация токена
        if serializer.is_valid(raise_exception=True):
            # Кастомный валидатор для проверки пароля

            if password_validator(password) is None:
                password = make_password(password)  # sha256 шифровка пароля
                credential = CustomUserLocalCredentials.objects.create(email=email,
                                                                       password=password,
                                                                       refresh_token=None,
                                                                       username=username)

                serializer = CustomUserSerializer(credential)
                token = RefreshToken.for_user(credential)   # Выписываем пару токенов
                access_token = token.access_token
                refresh_token = token
                credential.refresh_token = refresh_token  # Ссылка на зависимую таблицу с кредами для локального auth
                credential.save()
                #//TODO sha256 OTP
                user = CustomUser.objects.create(username=username,
                                                 auth_provider='local',
                                                 content_type=ContentType.objects.get_for_model(
                                                     CustomUserLocalCredentials),
                                                 object_id=credential.id,
                                                 email=email,
                                                 otp=str(randint(100000, 999999)))
                user.save()

                response = serializer.data
                response['access_token'] = str(access_token)    # Расширение запроса access-токеном т.к. он не хранится в БД
                return Response(data=response, status=status.HTTP_200_OK)


            return password_validator(password) # Возврат ошибки по паролю

        return Response("Ошибка сериализатора", status=status.HTTP_400_BAD_REQUEST)


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
        # Проверка полноты данных предоставленных в запросе и возврат кредов
        input_data = LocalUser(request=request).input_data_check()
        username = input_data.username
        password = input_data.password

        # Сериализаторы, которые пойдут под merge в конце для полноты предоставленных данных
        serializer = CustomUserSerializer(data=request.data)
        serializer.is_valid()
        user = CustomUser.objects.get_object_or_false(username=username)
        common_serializer_data = request.data
        common_serializer_data['object_id'] = user.object_id
        common_serializer_data['picture'] = user.picture
        common_serializer = UserSerializer(data=common_serializer_data)
        common_serializer.is_valid()

        # Шифрование пароля из запроса и получение шифрованного sha256 пароля из бд для проверки соответствия пароля
        credential = CustomUserLocalCredentials.objects.get(id=user.object_id)
        encrypted_password = credential.password.split('$') # Разбиение пароля по сегментам
        iterations = int(encrypted_password[1]) # 87000
        salt = encrypted_password[2].encode()
        secure_password = base64.b64encode(hashlib.pbkdf2_hmac('sha256', password.encode(), salt,
                                                               iterations, None)).decode("ascii").strip()

        # В случае успешной проверки пароля возвращаем юзеру его креды+токены
        if secure_password == encrypted_password[-1]:
            # Генерация новой пары токенов
            token = RefreshToken.for_user(credential)
            access_token = token.access_token
            refresh_token = token
            # Сохранение в БД refresh-tokenа
            credential.refresh_token = refresh_token
            credential.save()
            # Создание словаря response для кредов и общей информации о пользователе и мерж двух словарей
            response = serializer.data
            response['access_token'] = str(access_token)
            response['refresh_token'] = str(refresh_token)
            response.update(common_serializer.data)
            return Response(data=response, status=status.HTTP_200_OK)

        return Response('Неверный пароль', status=status.HTTP_403_FORBIDDEN)



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

        try:
            email = request.data['email']

        except:
            return Response('Отсутствует необходимое поле в теле запроса', status=status.HTTP_400_BAD_REQUEST)

        email_instance = CustomUserLocalCredentials.objects.get(email=email)
        serializer = CustomUserSerializer(instance=email_instance)
        send_mail('Код для восстановления пароля',
                  f'Ваш код для восстановления пароля - {serializer.data["otp"]}. Не передавайте его никому',
                  "root@bf13.by",
                  [f'{email}'],
                  fail_silently=False, )

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

    def get(self, request):

        client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        redirect_uri = 'https://bf13.by/users/auth/google-oauth2/complete'
        response_type = 'code'
        scope = 'email'
        access_type = 'offline'
        data = {'client_id': client_id,
                'redirect_uri': redirect_uri,
                'response_type': response_type,
                'scope': scope,
                'access_type': access_type}



class OAuth2Complete(APIView):

    def get(self, request):

        token_response = get_google_token(request)

        access_token = token_response['access_token']
        userinfo_headers = {'Authorization': 'Bearer ' + access_token}
        userinfo_response = requests.post(url="https://www.googleapis.com/oauth2/v3/userinfo", headers=userinfo_headers).json()
        username = userinfo_response['email'].rstrip('@gmail.com')
        email = userinfo_response['email']

        try:
            #//TODO GET EQ USERNAME
            # Проверка на наличие социального аккаунта в базе и возврат пары токенов в случае обращения
            data = get_social_user(username, access_token)
            return Response(data=data, status=status.HTTP_200_OK)
        except:
            # Создание записи в БД о новом социальном аккаунте, возврат пары токенов
            data = create_social_user(token_response, email, username, access_token)
            return Response(data=data, status=status.HTTP_200_OK)




class TelegramAuth(APIView):
    def post(self, request):
        data = request.data
        data_check_string = f'auth_date={data["auth_date"]}\nfirst_name={data["first_name"]}\nid={data["id"]}\nphoto_url={data["photo_url"]}\nusername={data["username"]}'.encode('utf-8')
        secret_key = hashlib.sha256('7754925216:AAGC16jCqaPOxHMo-jkCI6sPt_PPPWt08Lc'.encode('utf-8')).digest()
        signing_key = hmac.new(key=secret_key, msg=data_check_string, digestmod=hashlib.sha256).hexdigest()

        try:
            user = CustomUser.objects.get(username=data['username'])
            credentials = CustomUserTelegramCredentials.objects.get(id=user.object_id)
            data = {'id': credentials.user_id,
                    'first_name': credentials.first_name,
                    'username': user.username,
                    'photo_url': credentials.photo_url,
                    'auth_date': credentials.auth_date}
            if signing_key == credentials.hash:
                return Response(data=data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            credentials = CustomUserTelegramCredentials.objects.create(auth_date=data['auth_date'],
                                                                       hash=data['hash'],
                                                                       first_name=data['first_name'],
                                                                       photo_url=data['photo_url'],
                                                                       user_id=data['id'])
            user = CustomUser.objects.create(username=data['username'], auth_provider=['telegram'],
                                             object_id=credentials.id,
                                             content_type=ContentType.objects.get_for_model(
                                                     CustomUserTelegramCredentials),
                                             otp=str(randint(100000, 999999)))
            data['user_id'] = user.object_id
            return Response(data=data, status=status.HTTP_200_OK)

        return Response(data={"status": "login failed due to invalid data"}, status=status.HTTP_403_FORBIDDEN)
