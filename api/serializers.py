from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from . import services
from .models import Board, Elo, Game, Result


class EloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Elo
        fields = (
            "rating",
            "previous_rating",
            "wins",
            "losses",
            "draws",
            "uuid",
        )


class UserEloSerializer(serializers.ModelSerializer):
    elo = EloSerializer()

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "active",
            "elo",
        )


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = (
            "fen",
            "board_fen",
            "board_fen_flipped",
            "updated_at",
            "game_uuid",
        )


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = (
            "result",
            "termination",
        )


class GameSerializer(serializers.ModelSerializer):
    black_player = UserEloSerializer(required=False)
    white_player = UserEloSerializer(required=False)
    board = BoardSerializer(required=False)
    result = ResultSerializer(required=False)

    class Meta:
        model = Game
        fields = (
            "uuid",
            "black_player",
            "white_player",
            "created_at",
            "started_at",
            "finished_at",
            "board",
            "result",
        )

    def create(self, validated_data):
        result_data = validated_data.pop("result", {})
        board_data = validated_data.pop("board", {})

        preferred_color = self.context["request"].data.get(
            "preferred_color", "random")

        auth_username = self.context["request"].user

        game = services.create_game(
            result_data=result_data, board_data=board_data, **validated_data
        )

        services.assign_color(game, auth_username, preferred_color)

        return game


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data["name"] = self.user.username
        data["active"] = self.user.active

        return data
