import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.databases.models import Turns

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


@pytest.mark.django_db
class TestTurns:
    def set_up(self, turn_data):
        Turns.objects.create_turn(season=turn_data['season'], url=turn_data['url'], logo=turn_data['logo'],
                                  name=turn_data['name'], description=turn_data['description'],
                                  categories=turn_data['categories'], type=turn_data['type'])

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