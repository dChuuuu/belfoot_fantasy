from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .custom_methods import collect_data
from .custom_exceptions import IncompleteIdQueryException400
from .serializers import MatchesSerializer, TurnsSerializer, PlayersSerializer
from .models import Turns, Matches, Players
from ..custom_permissions import IsAdmin


@permission_classes([IsAuthenticated, IsAdmin])
class CRUDTurns(APIView):
    def post(self, request):
        data = collect_data(request, table_name='turns')
        turns_serializer = TurnsSerializer(data=data)
        if turns_serializer.is_valid(raise_exception=True):
            turn = Turns.objects.create_turn(data=data)
            data = turns_serializer.data
            data['id'] = turn.id
            return Response(data, status=status.HTTP_200_OK)
        return Response('Ошибка в запросе', status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            id = request.GET.get('id')
        except KeyError:
            raise IncompleteIdQueryException400
        turn = Turns.objects.get(id=id)
        turns_serializer = TurnsSerializer(instance=turn)
        return Response(turns_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        try:
            id = request.GET.get('id')
        except KeyError:
            raise IncompleteIdQueryException400
        columns = request.GET.keys()
        rows = []
        for column in columns:
            rows.append(request.GET.get(column))

        Turns.objects.update(id, columns, rows)
        turn = Turns.objects.get(id=id)
        turns_serializer = TurnsSerializer(instance=turn)
        return Response(data=turns_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        try:
            id = request.GET.get('id')
        except KeyError:
            raise IncompleteIdQueryException400
        Turns.objects.delete(id)
        return Response('Объект удалён', status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated, IsAdmin])
class CRUDMatches(APIView):
    def post(self, request):
        data = collect_data(request, table_name='matches')
        matches_serializer = MatchesSerializer(data=data)
        if matches_serializer.is_valid(raise_exception=True):
            match = Matches.objects.create_match(data=data)
            data = matches_serializer.data
            data['id'] = match.id
            return Response(data, status=status.HTTP_200_OK)
        return Response('Ошибка в запросе', status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            id = request.GET.get('id')
        except KeyError:
            raise IncompleteIdQueryException400
        match = Matches.objects.get(id=id)
        matches_serializer = MatchesSerializer(instance=match)
        return Response(matches_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        try:
            id = request.GET.get('id')
        except KeyError:
            raise IncompleteIdQueryException400
        columns = request.GET.keys()
        rows = []
        for column in columns:
            rows.append(request.GET.get(column))



        Matches.objects.update(id, columns, rows)
        match = Matches.objects.get(id=id)
        matches_serializer = MatchesSerializer(instance=match)
        return Response(matches_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        try:
            id = request.GET.get('id')
        except KeyError:
            raise IncompleteIdQueryException400
        Matches.objects.delete(id)
        return Response('Объект удалён', status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated, IsAdmin])
class CRUDPlayers(APIView):

    def post(self, request):
        data = collect_data(request, table_name='players')
        players_serializer = PlayersSerializer(data=data)
        if players_serializer.is_valid(raise_exception=True):
            player = Players.objects.create_player(data=data)
            data = players_serializer.data
            data['id'] = player.id
            return Response(data, status=status.HTTP_200_OK)
        return Response('Ошибка в запросе', status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        id = request.GET.get('id')

        if id is None:
            player = Players.objects.all()
            players_serializer = PlayersSerializer(data=player, many=True)
            players_serializer.is_valid()
            return Response(players_serializer.data, status=status.HTTP_200_OK)

        player = Players.objects.get(id=id)
        players_serializer = PlayersSerializer(instance=player)
        return Response(players_serializer.data, status=status.HTTP_200_OK)


    def patch(self, request):
        try:
            id = request.GET.get('id')
        except KeyError:
            raise IncompleteIdQueryException400
        columns = request.GET.keys()
        rows = request.GET.values()

        Players.objects.update(id, columns, rows)
        player = Players.objects.get(id=id)
        players_serializer = PlayersSerializer(instance=player)
        return Response(players_serializer.data, status=status.HTTP_200_OK)


    def delete(self, request):
        try:
            id = request.GET.get('id')
        except KeyError:
            raise IncompleteIdQueryException400
        Players.objects.delete(id)
        return Response('Объект удалён', status=status.HTTP_200_OK)

