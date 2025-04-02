import jwt
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from belfoot_fantasy import settings


@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def picture_url():
    return reverse('change_picture')

@pytest.fixture
def user_data():
    data = {"username": "test_username",
            "password": "test_password",
            "email": "test_email@example.com"}
    return data

@pytest.fixture
def register_url():
    return reverse('register_user')

@pytest.fixture
def register(register_url, client, user_data):
    response = client.post(register_url, user_data, format='json')
    return response

@pytest.fixture
def login_url():
    return reverse('login_user')

@pytest.fixture
def login(login_url, register, client, user_data):
    response = client.post(login_url, user_data, format='json')
    return response

@pytest.fixture
def picture_data():
    return 'picture'

@pytest.fixture
def change_username_url():
    return reverse('change_username')

@pytest.fixture
def get_info_url():
    return reverse('get_user_info')

@pytest.mark.django_db
class TestsProfiles:
    def test_picture(self, client, picture_url, picture_data, login):
        access_token = login.data['access_token']
        response = client.post(picture_url, data={'picture': f'{picture_data}'},
                               headers={'Authorization': f'Bearer {access_token}'})

        assert response.status_code == 200

    def test_change_username(self, client, change_username_url, register_url, user_data):

        response = client.post(register_url, user_data)
        access_token = response.data['access_token']
        response = client.post(change_username_url,
                               data={'username': 'changed_username'},
                               headers={'Authorization': f'Bearer {access_token}'})

        assert response.status_code == 200
        assert response.data['username'] == 'changed_username'

    def test_get_info(self, client, register, get_info_url):
        user_id = register.data['id']
        response = client.get(get_info_url + f'?user_id={user_id}')

        assert response.status_code == 200
        assert response.data is not None
