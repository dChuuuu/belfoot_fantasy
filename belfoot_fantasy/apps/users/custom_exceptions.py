from rest_framework.exceptions import APIException


class CustomUserException400(APIException):
    status_code = 400

    default_detail = {"message": "Неполные данные в теле запроса(username, password, email)"}