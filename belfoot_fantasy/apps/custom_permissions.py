import jwt
from django.conf import settings
from .users.models import CustomUser

class IsAdmin:

    def has_permission(self, request, *args):
        access_token = request.headers['Authorization'].lstrip('Bearer')
        user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                             algorithms=['HS256'], options={'verify_signature': False})['user_id']
        user = CustomUser.objects.get_object_or_false(object_id=user_id)
        if user.is_superuser is True:
            return True
        return False