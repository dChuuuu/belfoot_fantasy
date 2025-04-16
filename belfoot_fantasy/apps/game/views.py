import jwt
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import UsersCommands
from .serializers import UsersCommandsSerializer
from .custom_methods import Team
from belfoot_fantasy import settings

@permission_classes([IsAuthenticated])
class PlayersCommandsCRUD(APIView):

    def post(self, request):

        access_token = request.headers['Authorization'].lstrip('Bearer')
        user_id = jwt.decode(jwt=access_token, key=settings.SECRET_KEY,
                             algorithms=['HS256'], options={'verify_signature': False})['user_id']
        Team().is_valid(request, user_id)
        user = UsersCommands.objects.create_command(request, user_id)

        return Response('Запрос успешен', status=status.HTTP_200_OK)



