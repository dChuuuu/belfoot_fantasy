import jwt
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, DataError
from django.http import Http404

from ..users import models as user_model

from belfoot_fantasy import settings

from .custom_exceptions import WrongData400

# Create your models here.



class UsersCommands(models.Model):
    command_id = models.BigAutoField(primary_key=True, unique=True)
    command_staff = ArrayField(models.CharField(), blank=True, default=list)

    objects = models.Manager
