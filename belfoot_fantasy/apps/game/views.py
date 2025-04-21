import ast

import jwt
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .custom_exceptions import IncufficientCoins400, WrongPlayerID400, UnfilledInOutData400, PlayerError400
from .models import UsersCommands
from .serializers import UsersCommandsSerializer
from .custom_methods import Team
from ..databases.models import Players
from ..users import serializers as user_serializer
from belfoot_fantasy import settings
from ..users.models import CustomUser
from ..users.serializers import UserSerializer


@permission_classes([IsAuthenticated])
class PlayersCommandsCRUD(APIView):

    def post(self, request):

        access_token = request.headers['Authorization'].lstrip('Bearer')
        user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                             algorithms=['HS256'], options={'verify_signature': False})['user_id']

        user = Team().create_command(request, user_id)
        serializer = user_serializer.UserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        access_token = request.headers['Authorization'].lstrip('Bearer')
        user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                             algorithms=['HS256'], options={'verify_signature': False})['user_id']
        user = CustomUser.objects.get(object_id=user_id)
        command = UsersCommands.objects.get(command_id=user.command_id)

        try:
            players_out = request.data['out']
            players_in = request.data['in']
        except:
            raise UnfilledInOutData400

        command_temp = ast.literal_eval(command.command_staff[0])
        for player_out, player_in in zip(players_out, players_in):
            if (player_out not in command_temp['primary']) and (player_out not in command_temp['secondary']):
                raise PlayerError400
            else:
                print('YES', player_out, player_in)
                try:
                    command_temp['primary'][player_out] = command_temp['primary'][player_in]
                except:
                    command_temp['secondary'][player_out] = command_temp['secondary'][player_in]
                else:
                    raise PlayerError400

        request.data['command_staff'] = [command_temp]
        user = Team().create_command(request, user_id)
        serializer = user_serializer.UserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
class BuyPlayers(APIView):

    def post(self, request):
        access_token = request.headers['Authorization'].lstrip('Bearer')
        user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                             algorithms=['HS256'], options={'verify_signature': False})['user_id']

        try:
            players = request.data['players']
            user = CustomUser.objects.get(object_id=user_id)
            cost = 0
            players_temp = []
            for player_id in players:
                player = Players.objects.get(id=player_id)
                if str(player_id) not in user.players:
                    cost += player.cost
                    players_temp.append(int(player_id))

            if cost > user.coins:
                raise IncufficientCoins400

            user.coins -= cost
            user.players.extend(players_temp)
            user.save()
            serializer = UserSerializer(user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except KeyError:
            return Response('Не предоставлено поле players в теле запроса', status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            raise Http404
