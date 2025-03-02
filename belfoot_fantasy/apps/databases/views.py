from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .custom_methods import collect_data
from .custom_exceptions import IncompleteIdQueryException400
from serializers import MatchesSerializer, TurnsSerializer, PlayersSerializer
from .models import Turns, Matches, Players


class CRUDTurns(APIView):
    def post(self, request):
        data = collect_data(request, table_name='turns')
        turns_serializer = TurnsSerializer(data=data)
        if turns_serializer.is_valid(raise_exception=True):
            Turns.objects.create_turn(data=data)
            return Response(turns_serializer.data, status=status.HTTP_200_OK)
        return Response('Ошибка в запросе', status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            id = request.GET.get(id)
        except KeyError:
            raise IncompleteIdQueryException400
        turn = Turns.objects.get(id=id)
        turns_serializer = TurnsSerializer(instance=turn)
        if turns_serializer.is_valid(raise_exception=True):
            return Response(turns_serializer.data, status=status.HTTP_200_OK)
        return Response('Ошибка в запросе', status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        try:
            id = request.GET.get(id)
        except KeyError:
            raise IncompleteIdQueryException400
        columns = request.GET.keys()
        rows = request.GET.values()
        turn = Turns.objects.get(id=id)
        turns_serializer = TurnsSerializer(instance=turn)
        if turns_serializer.is_valid(raise_exception=True):
            turn.objects.update(id, columns, rows)
            turns_serializer = TurnsSerializer(instance=turn)
            return Response(turns_serializer.data, status=status.HTTP_200_OK)
        return Response('Ошибка в запросе', status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            id = request.GET.get(id)
        except KeyError:
            raise IncompleteIdQueryException400
        Turns.objects.delete(id)
        return Response('Объект удалён', status=status.HTTP_200_OK)

class CRUDMatches(APIView):
    def post(self, request):
        data = collect_data(request, table_name='matches')
        turns_serializer = TurnsSerializer(data=data)
        if turns_serializer.is_valid(raise_exception=True):
            Turns.objects.create(data=data)
            return Response(turns_serializer.data, status=status.HTTP_200_OK)
        return Response('Ошибка в запросе', status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            id = request.GET.get(id)
        except KeyError:
            raise IncompleteIdQueryException400
        match = Matches.objects.get(id=id)
        matches_serializer = MatchesSerializer(instance=match)
        if matches_serializer.is_valid(raise_exception=True):
            return Response(matches_serializer.data, status=status.HTTP_200_OK)
        return Response('Ошибка в запросе', status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        try:
            id = request.GET.get(id)
        except KeyError:
            raise IncompleteIdQueryException400
        columns = request.GET.keys()
        rows = request.GET.values()
        match = Matches.objects.get(id=id)
        matches_serializer = TurnsSerializer(instance=match)
        if matches_serializer.is_valid(raise_exception=True):
            match.objects.update(id, columns, rows)
            turns_serializer = TurnsSerializer(instance=match)
            return Response(turns_serializer.data, status=status.HTTP_200_OK)
        return Response('Ошибка в запросе', status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            id = request.GET.get(id)
        except KeyError:
            raise IncompleteIdQueryException400
        Matches.objects.delete(id)
        return Response('Объект удалён', status=status.HTTP_200_OK)


class CRUDPlayers(APIView):
    def post(self, request):
        data = collect_data(request, table_name='players')
        players_serializer = PlayersSerializer(data=data)
        if players_serializer.is_valid(raise_exception=True):
            Players.objects.create(data=data)
            return Response(players_serializer.data, status=status.HTTP_200_OK)
        return Response('Ошибка в запросе', status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            id = request.GET.get(id)
        except KeyError:
            raise IncompleteIdQueryException400
        player = Players.objects.get(id=id)
        players_serializer = PlayersSerializer(instance=player)
        if players_serializer.is_valid(raise_exception=True):
            return Response(players_serializer.data, status=status.HTTP_200_OK)
        return Response('Ошибка в запросе', status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        try:
            id = request.GET.get(id)
        except KeyError:
            raise IncompleteIdQueryException400
        columns = request.GET.keys()
        rows = request.GET.values()
        player = Players.objects.get(id=id)
        players_serializer = TurnsSerializer(instance=player)
        if players_serializer.is_valid(raise_exception=True):
            player.objects.update(id, columns, rows)
            players_serializer = TurnsSerializer(instance=player)
            return Response(players_serializer.data, status=status.HTTP_200_OK)
        return Response('Ошибка в запросе', status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            id = request.GET.get(id)
        except KeyError:
            raise IncompleteIdQueryException400
        Players.objects.delete(id)
        return Response('Объект удалён', status=status.HTTP_200_OK)
