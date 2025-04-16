import jwt
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, DataError
from django.http import Http404

from ..users import models as user_model

from belfoot_fantasy import settings

from .custom_exceptions import WrongData400

# Create your models here.
class UsersCommandsManager(models.Manager):
    def create_command(self, request, user_id):

        try:
            user = user_model.CustomUser.objects.get(object_id=user_id)

            if user.command_id:
                command = self.get(command_id=user.command_id)
                command.command_staff = request.data['command_staff']
                print(type(request.data['command_staff']))
                command.save()
            else:
                command = self.create(command_staff=request.data['command_staff'])
                command.save()
                user.command_id = command.command_id
                user.save()

        except ObjectDoesNotExist:
            raise Http404
        except DataError:
            raise WrongData400

        return user


class UsersCommands(models.Model):
    command_id = models.BigAutoField(primary_key=True, unique=True)
    command_staff = ArrayField(models.CharField(), blank=True, default=list)

    objects = UsersCommandsManager()
