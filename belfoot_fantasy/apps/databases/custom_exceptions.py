from rest_framework.exceptions import APIException


class WrongTableException400(APIException):
    status_code = 400

    default_detail = {"message": "Неверный <table_name> (backend)"}

class IncompleteDataException400(APIException):
    exception_data = []
    def __init__(self, exception_data=None):
        self.detail = {'message': f"Недостаточно данных в запросе. Данные:{exception_data}"}
    status_code = 400



class IncompleteIdQueryException400(APIException):
    status_code = 400

    default_detail = {'message': "Идентификатор не предоставлен в теле запроса"}