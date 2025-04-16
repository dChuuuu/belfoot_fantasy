from rest_framework.exceptions import APIException


class WrongData400(APIException):
    status_code = 400

    default_detail = {'message': "Неверный формат данных. Нужен массив[]"}


class WrongDict400(APIException):
    status_code = 400

    default_detail = {'message': 'Неверный формат данных. Нужен массив формата [{"primary": [<int>, <int>, <int>,'
                                     ' ..., <int>], "secondary": [<int>, <int>, <int>, ..., <int>]}]'}


class WrongPlayersCount400(APIException):
    status_code = 400

    default_detail = {'message': 'Неверное количество игроков. В основной команде должно быть 11 игроков,'
                                 ' в запасе 4 игрока'}


class WrongTeamPlayersCount400(APIException):
    status_code = 400

    default_detail = {'message': 'Не более 3 игроков из одной команды'}


class IncufficientCoins400(APIException):
    status_code = 400

    default_detail = {'message': 'Недостаточно монет'}