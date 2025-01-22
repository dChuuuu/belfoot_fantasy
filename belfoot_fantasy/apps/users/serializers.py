from .models import CustomUser, CustomUserTelegram

from rest_framework import serializers

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class CustomUserTelegramSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserTelegram
        fields = '__all__'