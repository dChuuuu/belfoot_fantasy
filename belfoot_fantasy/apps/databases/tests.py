import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import CustomUser, CustomUserLocalCredentials
from random import randint
from django.contrib.contenttypes.models import ContentType
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction


@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def turns_url():
    return reverse('crud_turns')

@pytest.fixture
def turn_data():
    data = {'season': 'spring',
            'url': 'example.com',
            'logo': 'base64string',
            'name': 'local tournament',
            'description': 'first in the year',
            'categories': 'football',
            'type': 'qualification'}
    return data


@pytest.fixture
def matches_url():
    return reverse('crud_matches')


@pytest.fixture
def matches_data():
    data = {'status': 'online',
            'time': '4:13',
            'datetime': '2024.01.01',
            'date_unix': 'unix',
            'score': '9999999'}
    return data


@pytest.fixture
def create_match(matches_data, matches_url, client):
    return client.post(matches_url, matches_data)


@pytest.fixture
def players_url():
    return reverse('crud_players')


@pytest.fixture
def players_data():
    data = {'name': 'Ivan Ivanov',
            'icon': 'b64_image',
            'number': '13',
            'url': 'example.com',
            'position': 'attack',
            'birthday': '18.02.1997',
            'country': 'Russia',
            'command': 'ДИНАМО',
            'cost': '1'}
    return data


@pytest.fixture
def admin_data():
    data = {"username": "test_username",
            "password": "tesA!1t_password",
            "email": "test_email@example.com",
            "secret_key": ":I0TJ;;;4sbHlLIo&T_{<hC4])W(&s?>iYVw{pe4rry#?0rP8AB+{Cv5RcN/I:L"}
    return data


@pytest.fixture
def user_data():
    data = {"username": "test_1username",
            "password": "tesA!1t_password",
            "email": "test_ema1il@example.com"}
    return data


@pytest.fixture
def admin_register_url():
    return reverse('register_admin')


@pytest.fixture
def user_register_url():
    return reverse('register_user')


@pytest.fixture
def admin_register(admin_register_url, client, admin_data):
    response = client.post(admin_register_url, admin_data, format='json')
    return response


@pytest.fixture
def user_register(user_register_url, client, user_data):
    response = client.post(user_register_url, user_data, format='json')
    return response


@pytest.fixture
def create_turn(turn_data, turns_url, client, admin_register):
    access_token = 'Bearer ' + admin_register.data['access_token']

    return client.post(turns_url, turn_data, headers={'Authorization': access_token}, format='json')


@pytest.fixture
def create_player(players_data, players_url, client):
    return client.post(players_url, players_data)


@pytest.fixture
def admin_setup():
    with transaction.atomic():
        credential = CustomUserLocalCredentials.objects.create(email="test_email@example.com",
                                                               password="tesA!1t_password",
                                                               refresh_token=None,
                                                               username="test_username")

        # Выписываем пару токенов

        # Ссылка на зависимую таблицу с кредами для локального auth
        credential.save()
        otp = str(randint(100000, 999999))

        user = CustomUser.objects.create(username="test_username",
                                         auth_provider='local',
                                         content_type=ContentType.objects.get_for_model(
                                             CustomUserLocalCredentials),
                                         object_id=credential.id,
                                         email="test_email@example.com",
                                         otp=otp,
                                         is_superuser=True)

        token = RefreshToken.for_user(user)
        access_token = token.access_token
        yield str(access_token)


@pytest.fixture
def user_setup():
    with transaction.atomic():
        credential = CustomUserLocalCredentials.objects.create(email="test_1email@example.com",
                                                               password="tesA!1t_password",
                                                               refresh_token=None,
                                                               username="test_1username")

        # Выписываем пару токенов

        # Ссылка на зависимую таблицу с кредами для локального auth
        credential.save()
        otp = str(randint(100000, 999999))

        user = CustomUser.objects.create(username="test_1username",
                                         auth_provider='local',
                                         content_type=ContentType.objects.get_for_model(
                                             CustomUserLocalCredentials),
                                         object_id=credential.id,
                                         email="test_1email@example.com",
                                         otp=otp,
                                         is_superuser=False)

        token = RefreshToken.for_user(user)
        access_token = token.access_token

        yield str(access_token)
        user.delete()
        user.save()
        credential.delete()
        credential.save()

admin_access_token = None
user_access_token = None


@pytest.mark.django_db
class TestTurns:

    def test_create(self, client, turns_url, turn_data, user_setup, admin_setup):
        # Проверка запроса админа на создание записи в БД о турнире
        access_token = 'Bearer ' + admin_setup
        admin_access_token = access_token
        response = client.post(turns_url, turn_data, headers={'Authorization': access_token}, format='json')
        assert response.status_code == 200

        # Проверка запроса с неполными данными
        del turn_data['season']
        response=client.post(turns_url, turn_data, headers={'Authorization': f'{access_token}'})
        assert response.status_code == 400

        # Проверка запроса обычного пользователя
        access_token = 'Bearer ' + user_setup
        user_access_token = access_token
        response = client.post(turns_url, turn_data, headers={'Authorization': f'{access_token}'})
        assert response.status_code == 403


    def test_get(self, client, turns_url, turn_data, admin_setup, user_setup):
        # Проверка на возможность получения данных админом
        access_token = 'Bearer ' + admin_setup
        response = client.post(turns_url, turn_data, headers={'Authorization': f'{access_token}'})
        turn_id = response.data["id"]
        response = client.get(turns_url + f'?id={turn_id}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 200

        # Проверка запроса с несуществующим id
        response = client.get(turns_url + f'?id={turn_id + 1}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 404

        # Проверка на возможность получения данных обычным пользователем
        access_token = 'Bearer ' + user_setup
        response = client.get(turns_url + f'?id={turn_id}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 200

    def test_patch(self, client, turns_url, turn_data, admin_setup, user_setup):

        # Проверка запроса с существующим id
        access_token = 'Bearer ' + admin_setup
        response = client.post(turns_url, turn_data, headers={'Authorization': f'{access_token}'})
        turn_id = response.data["id"]
        response = client.patch(turns_url + f'?id={turn_id}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 200

        # Проверка на изменение данных
        new_url = 'bf13.by'
        response = client.patch(turns_url + f'?id={turn_id}&url={new_url}', headers={'Authorization': f'{access_token}'})
        assert response.data['url'] == new_url

        # Проверка запроса с несуществующим id
        response = client.patch(turns_url + f'?id={turn_id + 1}&url={new_url}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 404

    def test_delete(self, client, turns_url, turn_data, admin_setup, user_setup):
        # Проверка запроса на удаление турнира с несуществующим id
        access_token = 'Bearer ' + admin_setup
        response = client.post(turns_url, turn_data, headers={'Authorization': f'{access_token}'})
        turn_id = response.data["id"]
        response = client.delete(turns_url + f'?id={turn_id + 1}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 404

        # Проверка запроса на удаление турнира обычным пользователем
        access_token = 'Bearer ' + user_setup
        response = client.delete(turns_url + f'?id={turn_id}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 403

        # Проверка запроса на удаление админом
        access_token = 'Bearer ' + admin_setup
        response = client.delete(turns_url + f'?id={turn_id}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 200


@pytest.mark.django_db
class TestMatches:

    def test_create(self, client, matches_url, matches_data, admin_setup, user_setup):
        # Проверка запроса на создание обычным пользователем
        access_token = 'Bearer ' + user_setup
        response = client.post(matches_url, matches_data, headers={'Authorization': f'{access_token}'})
        assert response.status_code == 403

        # Проверка запроса с полными данными
        access_token = 'Bearer ' + admin_setup
        response = client.post(matches_url, matches_data, headers={'Authorization': f'{access_token}'})
        assert response.status_code == 200

        # Проверка запроса с неполными данными
        del matches_data['status']
        response=client.post(matches_url, matches_data, headers={'Authorization': f'{access_token}'})
        assert response.status_code == 400

    def test_get(self, client, matches_url, matches_data, create_match, admin_setup, user_setup):
        # Проверка запроса на получение админом
        access_token = 'Bearer ' + admin_setup

        response = client.post(matches_url, matches_data, headers={'Authorization': f'{access_token}'})
        match_id = response.data['id']
        response = client.get(matches_url + f'?id={match_id}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 200

        # Проверка запроса на получение обычным пользователем
        access_token = 'Bearer ' + user_setup
        response = client.get(matches_url + f'?id={match_id}', headers={'Authorization': f'{access_token}'})

        # Проверка запроса с несуществующим id
        response = client.get(matches_url + f'?id={match_id + 1}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 404

    def test_patch(self, client, matches_url, matches_data, create_match, admin_setup, user_setup):
        # Проверка запроса на изменение админом
        access_token = 'Bearer ' + admin_setup
        response = client.post(matches_url, matches_data, headers={'Authorization': f'{access_token}'})
        match_id = response.data['id']
        new_status = 'offline'
        response = client.patch(matches_url + f'?id={match_id}&status={new_status}', headers={'Authorization': f'{access_token}'})
        assert response.data['status'] == new_status

        # Проверка на изменение несуществующим id
        response = client.patch(matches_url + f'?id={match_id + 1}&url={new_status}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 404

        # Проверка запроса на изменение обычным пользователем
        access_token = 'Bearer ' + user_setup
        response = client.patch(matches_url + f'?id={match_id}&status={new_status}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 403

    def test_delete(self, client, matches_url, matches_data, create_match, admin_setup, user_setup):
        # Проверка запроса на удаление с несуществующим id
        access_token = 'Bearer ' + admin_setup
        response = client.post(matches_url, matches_data, headers={'Authorization': f'{access_token}'})
        match_id = response.data['id']
        response = client.delete(matches_url + f'?id={match_id + 1}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 404

        # Проверка запроса на удаление обычным пользователем
        access_token = 'Bearer ' + user_setup
        response = client.delete(matches_url + f'?id={match_id}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 403

        # Проверка запроса на удаление админом
        access_token = 'Bearer ' + admin_setup
        response = client.delete(matches_url + f'?id={match_id}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 200


@pytest.mark.django_db
class TestPlayers:

    def test_create(self, client, players_url, players_data, admin_setup, user_setup):
        # Проверка запроса на создание обычным пользователем
        access_token = 'Bearer ' + user_setup
        response = client.post(players_url, players_data, headers={'Authorization': f'{access_token}'})
        assert response.status_code == 403

        # Проверка запроса на создание админом
        access_token = 'Bearer ' + admin_setup
        response = client.post(players_url, players_data, headers={'Authorization': f'{access_token}'})
        assert response.status_code == 200

        # Проверка запроса с неполными данными
        del players_data['birthday']
        response=client.post(players_url, players_data, headers={'Authorization': f'{access_token}'})
        assert response.status_code == 400

    def test_get(self, client, players_url, players_data, create_player, admin_setup, user_setup):
        # Проверка запроса админом
        access_token = 'Bearer ' + admin_setup
        response = client.post(players_url, players_data, headers={'Authorization': f'{access_token}'})
        player_id = response.data['id']
        response = client.get(players_url + f'?id={player_id}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 200

        # Проверка запроса обычным пользователем
        access_token = 'Bearer ' + user_setup
        response = client.get(players_url + f'?id={player_id}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 200

        # Проверка запроса с несуществующим id
        response = client.get(players_url + f'?id={player_id + 1}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 404

    def test_patch(self, client, players_url, players_data, create_player, admin_setup, user_setup):
        # Проверка запроса на изменение админом
        access_token = 'Bearer ' + admin_setup
        new_birthday = '09.03.1999'
        response = client.post(players_url, players_data, headers={'Authorization': f'{access_token}'})
        player_id = response.data['id']
        response = client.patch(players_url + f'?id={player_id}&birthday={new_birthday}',
                                headers={'Authorization': f'{access_token}'})
        assert response.data['birthday'] == new_birthday

        # Проверка запроса с несуществующим id
        response = client.patch(players_url + f'?id={player_id + 1}&url={new_birthday}',
                                headers={'Authorization': f'{access_token}'})
        assert response.status_code == 404

        # Проверка запроса на изменение обычным пользователем
        access_token = 'Bearer ' + user_setup
        response = client.patch(players_url + f'?id={player_id}&birthday={new_birthday}',
                                headers={'Authorization': f'{access_token}'})
        assert response.status_code == 403

    def test_delete(self, client, players_url, players_data, create_player, admin_setup, user_setup):
        # Проверка запроса на удаление с несуществующим id
        access_token = 'Bearer ' + admin_setup
        response = client.post(players_url, players_data, headers={'Authorization': f'{access_token}'})
        player_id = response.data['id']
        response = client.delete(players_url + f'?id={player_id + 1}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 404

        # Проверка запроса на удаление обычным пользователем
        access_token = 'Bearer ' + user_setup
        response = client.delete(players_url + f'?id={player_id + 1}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 403

        # Проверка запроса на удаление админом
        access_token = 'Bearer ' + admin_setup
        response = client.delete(players_url + f'?id={player_id}', headers={'Authorization': f'{access_token}'})
        assert response.status_code == 200