import ast

from django.core.exceptions import ObjectDoesNotExist
from django.db import DataError
from django.http import Http404

from .custom_exceptions import WrongData400, WrongDict400, WrongPlayersCount400, WrongTeamPlayersCount400, \
    IncufficientCoins400, WrongPlayerID400
from ..users import models as user_model
from .models import UsersCommands
from ..databases.models import Players
from ..users.models import CustomUser


class Team:
    def _collect(self, request):
        try:
            primary = request.data['command_staff'][0]['primary']
            secondary = request.data['command_staff'][0]['secondary']
            return [primary, secondary]
        except ValueError:
            raise WrongDict400

    def _amount_of_players(self, primary_command, secondary_command):
        if len(primary_command) != 11 or len(secondary_command) != 4:
            raise WrongPlayersCount400

    def _team_validator(self, primary_command, secondary_command, user_id):
        commands = {}
        user = CustomUser.objects.get(object_id=user_id)

        for player_id in primary_command:
            try:
                player = Players.objects.get(id=player_id)
                command = player.command
                commands[command] = commands.setdefault(command, 0) + 1
            except ObjectDoesNotExist:
                raise Http404

        for player_id in secondary_command:
            player = Players.objects.get(id=player_id)
            command = player.command
            commands[command] = commands.setdefault(command, 0) + 1



        if any(map(lambda player_count: player_count > 3, commands.values())):
            raise WrongTeamPlayersCount400

        return user

    def _is_player_available(self, user, request, command):

        command_temp = ast.literal_eval(command.command_staff[0])
        if (all(map(lambda player: str(player) in user.players, command_temp['primary'])) and
            all(map(lambda player: str(player) in user.players, command_temp['secondary']))):
            command.command_staff = request.data['command_staff']
            command.save()
            return user
        else:
            raise WrongPlayerID400


    def _validate(self, request, user):
        try:
            if user.command_id:
                command = UsersCommands.objects.get(command_id=user.command_id)
                user = self._is_player_available(user, request, command)
                return user

            else:
                command = UsersCommands.objects.create(command_staff=request.data['command_staff'])
                command.save()
                user = self._is_player_available(user, request, command)
                user.command_id = command.command_id
                user.save()
                return user

        except DataError:
            raise WrongData400

    def create_command(self, request, user_id):
        command = self._collect(request)
        primary_command, secondary_command = command[0], command[1]
        self._amount_of_players(primary_command, secondary_command)
        team_validator_list = self._team_validator(primary_command, secondary_command, user_id)

        user = team_validator_list
        user = self._validate(request, user)
        return user


