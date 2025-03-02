from .models import Turns, Matches, Players
from rest_framework import serializers

class MatchesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matches
        fields = '__all__'

class TurnsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turns
        fields = '__all__'

class PlayersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Players
        fields = '__all__'


