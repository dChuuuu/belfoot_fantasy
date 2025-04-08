from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import UsersCommands
from .serializers import UsersCommandsSerializer

@permission_classes([IsAuthenticated])
class PlayersCommandsCRUD(APIView):

    def post(self, request):
        user = UsersCommands.objects.create_command(request)
        return Response('Запрос успешен', status=status.HTTP_200_OK)

