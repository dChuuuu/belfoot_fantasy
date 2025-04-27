from .custom_exceptions import CustomUserException400


class LocalUser:
    def __init__(self, request=None, password=None, username=None, email=None, picture=None):
        self.request = request
        self.username = username
        self.password = password
        self.email = email
        self.picture = picture

    def __call__(self):
        return self.request

    def input_data_check(self):
        try:
            # Проверка на наличие нужных данных в теле запроса
            self.username = self.request.data['username']
            self.password = self.request.data['password']
            self.email = self.request.data['email']
            return self
        except KeyError:
            raise CustomUserException400

    def input_data_picture(self):
        try:
            self.picture = self.request.data['picture']
            return self
        except KeyError:
            raise CustomUserException400('Поле picture в теле запроса пустое')

    def input_data_username(self):
        try:
            self.username = self.request.data['username']
            return self
        except KeyError:
            raise CustomUserException400('Поле username в теле запроса пустое')

    def input_data_email(self):
        try:
            self.email = self.request.data['email']
            return self.email
        except KeyError:
            raise CustomUserException400('Поле email в теле запроса пустое')