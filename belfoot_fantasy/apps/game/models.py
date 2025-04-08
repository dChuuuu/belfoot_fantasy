import jwt
from django.db import models
from ..users import models as user_model
from belfoot_fantasy import settings


# Create your models here.
class UsersCommandsManager(models.Manager):
    def create_command(self, request):
        access_token = request.headers['Authorization'].lstrip('Bearer')
        user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                                        algorithms=['HS256'], options={'verify_signature': False})['user_id']
        user = user_model.CustomUser.objects.get(object_id=user_id)

        return user


class UsersCommands(models.Model):
    command_id = models.BigAutoField(primary_key=True, unique=True)
    command_staff = models.JSONField()

    objects = UsersCommandsManager()
