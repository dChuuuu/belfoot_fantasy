import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def user_data():
    data = {"username": "test_username",
            "password": "test_password",
            "email": "test_email@example.com"}
    return data

@pytest.fixture
def register_user(client, register_user_url, user_data):
    response = client.post(register_user_url, user_data)
    return response

@pytest.fixture
def register_user_url():
    return reverse('register_user')

@pytest.fixture
def login_user_url():
    return reverse('login_user')

@pytest.mark.django_db
class TestJWT:

    def test_register(self, client, user_data, register_user_url):
        response = client.post(register_user_url, user_data)

        assert response.status_code == 200
        assert response.data['access_token']
        assert response.data['refresh_token']

    def test_login_successful(self, client, user_data, register_user, login_user_url):
        response = client.post(login_user_url, user_data)

        assert response.status_code == 200