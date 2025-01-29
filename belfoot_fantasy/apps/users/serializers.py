from .models import CustomUser, CustomUserLocalCredentials  # , CustomUserTelegram

from rest_framework import serializers

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserLocalCredentials
        fields = '__all__'

# class CustomUserTelegramSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUserTelegram
#         fields = '__all__'