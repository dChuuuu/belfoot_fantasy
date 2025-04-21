from .models import UsersCommands
from rest_framework import serializers

class UsersCommandsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersCommands
        fields = '__all__'