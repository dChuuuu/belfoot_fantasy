from django.shortcuts import render
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


@permission_classes([IsAuthenticated])
class PlayersCommandsCRUD(APIView):

    def post(self, request):
        pass
