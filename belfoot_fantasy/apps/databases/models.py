from django.db import models

# Create your models here.

class Players(models.Model):

    id = models.BigAutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=32)
    icon = models.TextField()
    number = models.IntegerField()
    url = models.TextField()
    position = models.CharField(max_length=32)
    birthday = models.DateField()
    country = models.CharField(max_length=32)


class Turns(models.Model):

    id = models.BigAutoField(primary_key=True, unique=True)
    season = models.CharField(max_length=32)
    url = models.TextField()
    logo = models.TextField()
    name = models.CharField(max_length=32)
    description = models.TextField()
    name_turn = models.CharField(max_length=32)
    categories = models.CharField(max_length=32)
    tags = models.CharField(max_length=32)
    type = models.CharField(max_length=32)


class Matches(models.Model):

    id = models.BigAutoField(primary_key=True, unique=True)
    status = models.CharField(max_length=32)
    time = models.CharField(max_length=32)
    date = models.DateField(max_length=32)
    date_api = models.TextField()
    date_unix = models.DateTimeField()
    score = models.CharField(max_length=32)
