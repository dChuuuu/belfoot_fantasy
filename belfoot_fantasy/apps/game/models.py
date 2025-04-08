from django.db import models

# Create your models here.

class UsersCommand(models.Model):
    command_id = models.BigAutoField(primary_key=True, unique=True)
    command_staff = models.JSONField()
