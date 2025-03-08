from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import Http404


class Manager(models.Manager):
    def get(self, id):
        try:
            turn = models.Manager.get(self, id=id)
            return turn
        except ObjectDoesNotExist:
            raise Http404

    def update(self, id, columns, rows):
        try:
            turn = self.get(id=id)
            for column, row in zip(columns, rows):
                setattr(turn, column, row)
                turn.save()
        except ObjectDoesNotExist:
            raise Http404

    def delete(self, id):
        try:
            turn = models.Manager.get(self, id=id)
            turn.delete()
        except ObjectDoesNotExist:
            raise Http404


class PlayersManager(Manager):
    def create_player(self, data):
        self.create(name=data['name'],
                    icon=data['icon'],
                    number=data['number'],
                    url=data['url'],
                    position=data['position'],
                    birthday=data['birthday'],
                    country=data['country'])


class TurnsManager(Manager):
    def create_turn(self, data):
        self.create(season=data['season'],
                    url=data['url'],
                    logo=data['url'],
                    name=data['name'],
                    description=data['description'],
                    categories=data['categories'],
                    type = data['type'])


class MatchesManager(Manager):
    def create_match(self, data):
        self.create(status=data['status'],
                    datetime=data['datetime'],
                    date_unix=data['date_unix'],
                    score=data['score'])



class Turns(models.Model):

    id = models.BigAutoField(primary_key=True, unique=True)
    season = models.CharField(max_length=32)
    url = models.TextField()
    logo = models.TextField()
    name = models.CharField(max_length=32)
    description = models.TextField()
    categories = models.CharField(max_length=32)
    type = models.CharField(max_length=32)

    objects = TurnsManager()


class Matches(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    status = models.CharField(max_length=32)
    datetime = models.TextField()
    date_unix = models.TextField()
    score = models.CharField(max_length=32)

    objects = MatchesManager()


class Players(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=32)
    icon = models.TextField()
    number = models.TextField()
    url = models.TextField()
    position = models.CharField(max_length=32)
    birthday = models.CharField()
    country = models.CharField(max_length=32)

    objects = PlayersManager()
