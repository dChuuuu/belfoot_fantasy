import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


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
def create_turn(turn_data, turns_url, client):
    return client.post(turns_url, turn_data)

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
            'country': 'Russia'}
    return data

@pytest.fixture
def create_player(players_data, players_url, client):
    return client.post(players_url, players_data)


@pytest.mark.django_db
class TestTurns:

    def test_create(self, client, turns_url, turn_data):
        # Проверка запроса с полными данными
        response = client.post(turns_url, turn_data)
        assert response.status_code == 200
        # Проверка запроса с неполными данными
        del turn_data['season']
        response=client.post(turns_url, turn_data)
        assert response.status_code == 400

    def test_get(self, client, turns_url, turn_data, create_turn):
        # Проверка запроса с существующим id
        response = client.get(turns_url + f'?id={create_turn.data["id"]}')
        assert response.status_code == 200
        # Проверка запроса с несуществующим id
        response = client.get(turns_url + f'?id={create_turn.data["id"] + 1}')
        assert response.status_code == 404

    def test_patch(self, client, turns_url, turn_data, create_turn):
        # Проверка запроса с существующим id
        new_url = 'bf13.by'
        response = client.patch(turns_url + f'?id={create_turn.data["id"]}&url={new_url}')
        assert response.data['url'] == new_url
        # Проверка запроса с несуществующим id
        response = client.patch(turns_url + f'?id={create_turn.data["id"] + 1}&url={new_url}')
        assert response.status_code == 404

    def test_delete(self, client, turns_url, turn_data, create_turn):
        # Проверка запроса с существующим id
        response = client.delete(turns_url + f'?id={create_turn.data["id"] + 1}')
        assert response.status_code == 404
        # Проверка запроса с существующим id
        response = client.delete(turns_url + f'?id={create_turn.data["id"]}')
        assert response.status_code == 200


@pytest.mark.django_db
class TestMatches:

    def test_create(self, client, matches_url, matches_data):
        # Проверка запроса с полными данными
        response = client.post(matches_url, matches_data)
        assert response.status_code == 200
        # Проверка запроса с неполными данными
        del matches_data['status']
        response=client.post(matches_url, matches_data)
        assert response.status_code == 400

    def test_get(self, client, matches_url, matches_data, create_match):
        # Проверка запроса с существующим id
        response = client.get(matches_url + f'?id={create_match.data["id"]}')
        assert response.status_code == 200
        # Проверка запроса с несуществующим id
        response = client.get(matches_url + f'?id={create_match.data["id"] + 1}')
        assert response.status_code == 404

    def test_patch(self, client, matches_url, matches_data, create_match):
        # Проверка запроса с существующим id
        new_status = 'offline'
        response = client.patch(matches_url + f'?id={create_match.data["id"]}&status={new_status}')
        assert response.data['status'] == new_status
        # Проверка запроса с несуществующим id
        response = client.patch(matches_url + f'?id={create_match.data["id"] + 1}&url={new_status}')
        assert response.status_code == 404

    def test_delete(self, client, matches_url, matches_data, create_match):
        # Проверка запроса с существующим id
        response = client.delete(matches_url + f'?id={create_match.data["id"] + 1}')
        assert response.status_code == 404
        # Проверка запроса с существующим id
        response = client.delete(matches_url + f'?id={create_match.data["id"]}')
        assert response.status_code == 200


@pytest.mark.django_db
class TestPlayers:

    def test_create(self, client, players_url, players_data):
        # Проверка запроса с полными данными
        response = client.post(players_url, players_data)
        assert response.status_code == 200
        # Проверка запроса с неполными данными
        del players_data['birthday']
        response=client.post(players_url, players_data)
        assert response.status_code == 400

    def test_get(self, client, players_url, players_data, create_player):
        # Проверка запроса с существующим id
        response = client.get(players_url + f'?id={create_player.data["id"]}')
        assert response.status_code == 200
        # Проверка запроса с несуществующим id
        response = client.get(players_url + f'?id={create_player.data["id"] + 1}')
        assert response.status_code == 404

    def test_patch(self, client, players_url, players_data, create_player):
        # Проверка запроса с существующим id
        new_birthday = '09.03.1999'
        response = client.patch(players_url + f'?id={create_player.data["id"]}&birthday={new_birthday}')
        assert response.data['birthday'] == new_birthday
        # Проверка запроса с несуществующим id
        response = client.patch(players_url + f'?id={create_player.data["id"] + 1}&url={new_birthday}')
        assert response.status_code == 404

    def test_delete(self, client, players_url, players_data, create_player):
        # Проверка запроса с существующим id
        response = client.delete(players_url + f'?id={create_player.data["id"] + 1}')
        assert response.status_code == 404
        # Проверка запроса с существующим id
        response = client.delete(players_url + f'?id={create_player.data["id"]}')
        assert response.status_code == 200