from django.db import models

from django.db.models import DateTimeField


class Game(models.Model):
    start_timestamp = models.DateTimeField(auto_now_add=True)
    end_timestamp = models.DateTimeField()


class Board(models.Model):
    pass


class Move(models.Model):
    pass


class Piece(models.Model):
    pass


class Result(models.Model):
    pass


class Claim(models.Model):
    pass


class ClaimItem(models.Model):
    pass


