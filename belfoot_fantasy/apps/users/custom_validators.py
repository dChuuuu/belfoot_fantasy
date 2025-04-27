import re

from rest_framework import status
from rest_framework.response import Response


def password_validator(password):
    if len(password) > 36:
        return Response({"ошибка": "слишком длинный пароль"}, status=status.HTTP_403_FORBIDDEN)

    if len(password) < 8:
        return Response({"ошибка": "слишком короткий пароль"}, status=status.HTTP_403_FORBIDDEN)

    if re.search(r'[A-Z]', password) is False:
        return Response({"ошибка": "пароль должен содержать заглавную букву"}, status=status.HTTP_403_FORBIDDEN)

    if re.search(r'[!@#$%^&]', password) is False:
        return Response({"ошибка": "пароль должен содержать хотя бы один из следующих символов: !@#$%^&"})

    if re.search(r'[0123456789]', password) is False:
        return Response({"ошибка": "пароль должен содержать хотя бы одну цифру"})

