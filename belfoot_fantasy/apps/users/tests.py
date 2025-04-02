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
def user_data_custom():
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

@pytest.fixture
def login_user(client, register_user, login_user_url, user_data):
    response = client.post(login_user_url, user_data, format='json')
    return response

@pytest.fixture
def secured_view_url():
    return reverse('test_secured_view')


@pytest.mark.django_db
class TestAuth:

    def test_register(self, client, user_data, register_user_url):

        response = client.post(register_user_url, user_data)

        assert response.status_code == 200
        assert response.data['access_token']
        assert response.data['refresh_token']

        user_data['username'] = ''
        user_data['email'] = ''
        user_data['password'] = ''
        response = client.post(register_user_url, user_data)

        assert response.status_code == 403


    def test_login(self, client, user_data, user_data_custom, register_user, login_user_url):

        response = client.post(login_user_url, user_data_custom, format='json')

        assert response.status_code == 200
        assert response.data['access_token']
        assert response.data['refresh_token']

        user_data_custom['password'] = 'None'
        response = client.post(login_user_url, user_data_custom, format='json')

        assert response.status_code == 403

        user_data_custom = user_data
        user_data_custom['username'] = 'None'
        response = client.post(login_user_url, user_data_custom, format='json')

        assert response.status_code == 404

        user_data_custom = user_data
        user_data_custom['username'] = 'test_username'
        user_data_custom['password'] = ''
        response = client.post(login_user_url, user_data_custom, format='json')

        assert response.status_code == 403

    def test_jwt_auth(self, client, login_user, secured_view_url):
        access_token = login_user.data['access_token']
        response = client.get(secured_view_url, headers={'Authorization': f'Bearer {access_token}'})

        assert response.status_code == 200

        access_token += '1'
        response = client.get(secured_view_url, headers={'Authorization': f'Bearer {access_token}'})

        assert response.status_code == 401

    def test_refreshing_token(self, client, user_data, login_user):
        access_token = login_user.data['access_token']
        refresh_token = login_user.data['refresh_token']
        response = client.post(reverse('token_refresh'),
                               headers={'Authorization': f'Bearer {access_token}'},
                               data={'refresh': refresh_token},
                               format='json')

        assert response.status_code == 200
