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


class WrongPlayerID400(APIException):
    status_code = 400

    default_detail = {'message': 'Игрока нет в наличии у пользователя'}


class PlayerError400(APIException):
    status_code = 400

    default_detail = {'message': 'Ошибка игрока(возможно нет в команде)'}

class UnfilledInOutData400(APIException):
    status_code = 400

    default_detail = {'message': 'Не предоставлены данные in: [], out: [] в теле запроса'}