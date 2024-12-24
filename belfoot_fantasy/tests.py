# from http.cookies import SimpleCookie
#
# import pytest
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APIClient
#
# from apps.users.models import CustomUser
#
#
# # Фикстура клиента
# @pytest.fixture
# def client():
#     return APIClient()
#
# # Фикстуры урлов
# @pytest.fixture
# def register_url():
#     return reverse('register_user')
#
#
# @pytest.fixture
# def login_url():
#     return reverse('login_user')
#
# @pytest.fixture
# def reset_password_url():
#     return reverse('reset_password')
#
# @pytest.fixture
# def ban_user_url():
#     return reverse('ban_user')
#
# @pytest.fixture
# def logout_user_url():
#     return reverse('logout_user')
#
#
# @pytest.fixture
# def token_check():
#     return reverse('token_check')
#
#
# # Фикстуры пользовательских данных
# @pytest.fixture
# def full_user_data():
#     return {'username': "user1", 'password': "user's1_password", 'email': "test@example.com"}
#
#
# # Фикстуры регистрации и успешного логина
# @pytest.fixture
# def register_user(client, full_user_data, register_url):
#     return client.post(path=register_url, data=full_user_data)
#
#
# # Проверка функциональности
# @pytest.mark.django_db
# class TestLogin:
#
#     def test_successful_auth(self, client, register_url, login_url, full_user_data, token_check):
#         '''Тестовый кейс для успешной попытки логина. Все данные верны'''
#         response_register = client.post(path=register_url, data=full_user_data)
#         response_login = client.post(path=login_url, data=full_user_data)
#         assert response_register.status_code == status.HTTP_200_OK # Успешная регистрация
#         assert response_login.status_code == status.HTTP_200_OK # Успешный логин
#
#     def test_unaccepted_data(self, client, register_user, login_url):
#         '''Тестовый кейс, описывающий неверные данные при логине'''
#         response_register = register_user
#         data = {'username': "user1", 'password': "user's1_passsword"}
#         wrong_password = client.post(path=login_url, data=data)
#         data = {'username': "user2231", 'password': "user's1_password"}
#         wrong_username = client.post(path=login_url, data=data)
#         assert wrong_password.status_code == status.HTTP_403_FORBIDDEN # Кейс с неверным паролем
#         assert wrong_username.status_code == status.HTTP_404_NOT_FOUND # Кейс с неверным юзернеймом
#
#     def test_token_check(self, client, register_user, token_check, full_user_data):
#         '''Тестовый кейс, описывающий работу с токенами'''
#         response_register = register_user
#         access_token = response_register.cookies['access_token'].value
#         refresh_token = response_register.cookies['refresh_token'].value
#         client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
#         response_token_auth_full = client.post(path=token_check, data=full_user_data, format='json')
#         assert response_token_auth_full.status_code == status.HTTP_200_OK # Кейс успешной проверки. Токены даются как положено
#
#
#         cookies = {'refresh_token': refresh_token}
#         access_token = 'sadasdasd'
#         client.cookies = SimpleCookie(cookies)
#         client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
#         response_token_auth_refresh = client.post(path=token_check, data=full_user_data, format='json')
#         assert response_token_auth_refresh.status_code == status.HTTP_200_OK # Кейс с неверным access-token. Генерация новой пары
#
#
#         cookies = {'refresh_token': 'asdawdasd'}
#         access_token = 'sadasdasd'
#         client.cookies = SimpleCookie(cookies)
#         client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
#         response_token_auth_null = client.post(path=token_check, data=full_user_data, format='json')
#         assert response_token_auth_null.status_code == status.HTTP_403_FORBIDDEN # Кейс с неверной парой. Повторная авторизация необходима
#
#     def test_reset_password(self, client, register_user, full_user_data, reset_password_url):
#         '''Тестовый кейс, описывающий сброс пароля'''
#         response_register = register_user
#         email = full_user_data['email']
#         user = CustomUser.objects.get(email=email)
#         otp = user.otp
#         username = full_user_data['username']
#         data = {'email': email,
#                 'otp': otp,
#                 'new_password': 'sadasd'}
#         response_reset_password = client.post(path=reset_password_url, data=data)
#         new_password_instance = CustomUser.objects.get(email=email)
#         new_password = new_password_instance.password
#
#         assert response_reset_password.status_code == status.HTTP_200_OK # Проверка успешности сброса пароля
#         assert new_password == data['new_password'] # Проверка соответствия нового пароля заданному
#
#     def test_logout(self, client, register_user, login_url, full_user_data, logout_user_url, token_check):
#         '''Тестовый кейс, описывающий функционал логаута'''
#         response_register = register_user
#         response_logout = client.post(path=logout_user_url)
#         assert response_logout.status_code == status.HTTP_200_OK # Проверка успешного логаута
#
#
#     def test_banned_user(self, client, register_user, full_user_data, token_check, ban_user_url):
#         '''Тестовый кейс, описывающий функционал бана'''
#         response_register = register_user
#         username = full_user_data['username']
#         data = {'username': username}
#         response_banned = client.post(path=ban_user_url, data=data)
#
#         assert response_banned.status_code == status.HTTP_200_OK # Проверка успешного бана
#
#         response_token_check = client.post(path=token_check, data=data, format='json')
#
#         assert response_token_check.status_code == status.HTTP_403_FORBIDDEN # Попытка получения доступа с баном