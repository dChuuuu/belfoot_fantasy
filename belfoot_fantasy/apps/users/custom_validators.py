import re

from rest_framework import status
from rest_framework.response import Response

from .custom_exceptions import TooLongPassword400, TooShortPassword400, UpperCasePassword400, SymbolPassword400, \
    DigitPassword400, LowerCasePassword400


def password_validator(password):
    if len(password) > 36:
        raise TooLongPassword400

    if len(password) < 8:
        raise TooShortPassword400

    if re.search(r'[A-Z]', password) is None:
        print(password)
        raise UpperCasePassword400

    if re.search(r'[a-z]', password) is None:
        raise LowerCasePassword400

    if re.search(r'[!@#$%^&]', password) is None:
        raise SymbolPassword400

    if re.search(r'[0123456789]', password) is None:
        raise DigitPassword400

