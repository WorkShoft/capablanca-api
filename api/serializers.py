import uuid
import chess
from rest_framework import serializers

from .models import Game, Result, Board, Player


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ('fen', 'updated_at', 'game_uuid')


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ('description',)


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player

        fields = ('user', 'uuid',)


class GameSerializer(serializers.ModelSerializer):
    blacks_player = PlayerSerializer(required=False)
    whites_player = PlayerSerializer(required=False)
    board = BoardSerializer(required=False)
    result = ResultSerializer(required=False)

    class Meta:
        model = Game
        fields = ('uuid', 'blacks_player', 'whites_player',
                  'start_timestamp', 'end_timestamp',
                  'board', 'result',
                  )

    def create(self, validated_data):
        #user = self.context['request'].user

        board_data = validated_data.pop('board', {})
        result_data = validated_data.pop('result', {})
        blacks_player_data = validated_data.pop('blacks_player', {})
        whites_player_data = validated_data.pop('whites_player', {})

        blacks_player_object = Player.objects.create(**blacks_player_data)
        whites_player_object = Player.objects.create(**whites_player_data)

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
            blacks_player=blacks_player_object,
            whites_player=whites_player_object,
            uuid=game_uuid,
            ** validated_data
        )

        return game
