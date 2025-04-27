from .models import CustomUser, CustomUserLocalCredentials  # , CustomUserTelegram

from rest_framework import serializers

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserLocalCredentials
        fields = ['email', 'username', 'refresh_token', 'id']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'auth_provider', 'object_id', 'email', 'picture', 'command_id', 'players', 'refresh_token']

# class CustomUserTelegramSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUserTelegram
#         fields = '__all__'