import uuid

import chess
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Game, Result, Board


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('username', 'active',)


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ('fen', 'updated_at', 'game_uuid')


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ('description',)


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
        board_data = validated_data.pop('board', {})
        result_data = validated_data.pop('result', {})

        preferred_color = self.context['request'].data.get(
            'preferred_color', 'random')

        game_uuid = uuid.uuid4()

        game_board = chess.Board()
        fen = game_board.fen()
        board_object = Board.objects.create(
            **board_data, fen=fen, game_uuid=game_uuid)

        result_object = Result.objects.create(
            **result_data, description=Result.IN_PROGRESS)

        game = Game.objects.create(
            result=result_object,
            board=board_object,
            uuid=game_uuid,
            **validated_data
        )

        auth_username = self.context['request'].user

        game.assign_color(auth_username, preferred_color)

        return game
