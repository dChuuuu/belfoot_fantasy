from rest_framework.exceptions import APIException


class TooLongPassword400(APIException):
    status_code = 400

    default_detail = {'message': "Слишком длинный пароль(не более 36 символов)"}


class TooShortPassword400(APIException):
    status_code = 400

    default_detail = {'message': "Слишком короткий пароль(не менее 8 символов)"}


class UpperCasePassword400(APIException):
    status_code = 400

    default_detail = {'message': "Пароль должен содержать хотя бы одну заглавную букву"}


class LowerCasePassword400(APIException):
    status_code = 400

    default_detail = {'message': "Пароль должен содержать хотя бы одну строчную букву"}


class SymbolPassword400(APIException):
    status_code = 400

    default_detail = {'message': "Пароль должен содержать хотя бы один спецсимвол !@#$%^&"}


class DigitPassword400(APIException):
    status_code = 400

    default_detail = {'message': "Пароль должен содержать хотя бы одну цифру"}