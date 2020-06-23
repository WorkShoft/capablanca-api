from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Game, Result, Board
from . import services


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('username', 'active',)


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ('fen', 'board_fen', 'updated_at', 'game_uuid',)


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ('result', 'termination',)


class GameSerializer(serializers.ModelSerializer):
    blacks_player = UserSerializer(required=False)
    whites_player = UserSerializer(required=False)
    board = BoardSerializer(required=False)
    result = ResultSerializer(required=False)

    class Meta:
        model = Game
        fields = (
            'uuid', 'blacks_player', 'whites_player',
            'created_at', 'started_at', 'finished_at',
            'board', 'result',
        )

    def create(self, validated_data):
        result_data = validated_data.pop('result', {})
        board_data = validated_data.pop('board', {})

        preferred_color = self.context['request'].data.get(
            'preferred_color', 'random'
        )

        auth_username = self.context['request'].user

        game = services.create_game(
            result_data=result_data, board_data=board_data, **validated_data
        )

        services.assign_color(game, auth_username, preferred_color)

        return game
