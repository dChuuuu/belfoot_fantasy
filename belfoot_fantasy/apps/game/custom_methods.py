from django.core.exceptions import ObjectDoesNotExist
from django.db import DataError
from django.http import Http404

from .custom_exceptions import WrongData400, WrongDict400, WrongPlayersCount400, WrongTeamPlayersCount400, \
    IncufficientCoins400
from ..users import models as user_model
from .models import UsersCommands
from ..databases.models import Players
from ..users.models import CustomUser


class Team:
    def _collect(self, request):
        try:
            primary = request.data[0]['primary']
            secondary = request.data[0]['secondary']
            return [primary, secondary]
        except ValueError:
            raise WrongDict400

    def _amount_of_players(self, primary_command, secondary_command):
        if len(primary_command) != 11 or len(secondary_command) != 4:
            raise WrongPlayersCount400

    def _team_validator(self, primary_command, secondary_command, user_id):
        commands = {}
        cost = 0
        user = CustomUser.objects.get(object_id=user_id)
        for player_id in primary_command:
            try:
                player = Players.objects.get(id=player_id)
                command = player.command
                cost += player.cost
                commands.setdefault(command, 0) + 1
            except ObjectDoesNotExist:
                raise Http404

        for player_id in secondary_command:
            player = Players.objects.get(id=player_id)
            command = player.command
            cost += player.cost
            commands.setdefault(command, 0) + 1

        if any(map(lambda player_count: player_count > 3, commands)):
            raise WrongTeamPlayersCount400

        if cost > user.coins:
            raise IncufficientCoins400

        return [cost, user]
        # user.coins -= cost
        # user.save()

    def _validate(self, request, user_id, user):

        try:

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

        except DataError:
            raise WrongData400

        return user

    def is_valid(self, request, user_id):
        command = self._collect(request)
        primary_command, secondary_command = command[0], command[1]
        self._amount_of_players(primary_command, secondary_command)
        team_validator_list = self._team_validator(primary_command, secondary_command, user_id)
        cost = team_validator_list[0]
        user = team_validator_list[1]

