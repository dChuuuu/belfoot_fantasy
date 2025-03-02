from rest_framework.exceptions import APIException


class WrongTableException400(APIException):
    status_code = 400

    default_detail = {"message": "Неверный <table_name> (backend)"}

class IncompleteDataException400(APIException):
    def __init__(self, data_list):
        self.data_list = data_list

    def get_data_list(self):
        return self.data_list

    data_list = get_data_list()
    status_code = 400

    default_detail = {'message': f"Недостаточно данных в запросе. Данные:{data_list}"}


class IncompleteIdQueryException400(APIException):
    status_code = 400

    default_detail = {'message': "Идентификатор не предоставлен в теле запроса"}