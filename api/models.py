import chess
import uuid
import random

from django.db.models import Model, IntegerField, CharField, TextField, DateTimeField, BooleanField, UUIDField, OneToOneField, ForeignKey, CASCADE
from django.conf import settings


class Elo(Model):
    """
    https://en.wikipedia.org/wiki/Elo_rating_system#Mathematical_details
    """

    rating = IntegerField(default=1200)
    k_factor = IntegerField(default=32)
    wins = IntegerField(default=0)
    losses = IntegerField(default=0)
    draws = IntegerField(default=0)
    updated_at = DateTimeField(auto_now=True)

    player = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        null=True
    )


class Result(Model):
    """
    Holds result and termination data following the PGN spec
    result: declares the winner
    termination: gives additional data about the result
    http://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm#c9.8.1
    """

    # RESULT
    WHITE_WINS = "White wins"
    BLACK_WINS = "Black wins"
    DRAW = "Draw"
    IN_PROGRESS = "In progress"

    # TERMINATION
    ABANDONED = "Abandoned"
    ADJUDICATION = "Adjudication"
    DEATH = "Death"
    EMERGENCY = "Emergency"
    NORMAL = "Normal"
    RULES_INFRACTION = "Rules infraction"
    TIME_FORFEIT = "Time forfeit"
    UNTERMINATED = "Unterminated"

    RESULT_CHOICES = [
        (WHITE_WINS, "White wins"),
        (BLACK_WINS, "Black wins"),
        (DRAW, "Drawn game"),
        (IN_PROGRESS, "Game still in progress, game abandoned, or result otherwise unknown"),
    ]

    TERMINATION_CHOICES = [
        (ABANDONED, "Abandoned game."),
        (ADJUDICATION, "Result due to third party adjudication process."),
        (DEATH, "One or both players died during the course of this game."),
        (EMERGENCY, "Game concluded due to unforeseen circumstances."),
        (NORMAL, "Game terminated in a normal fashion."),
        (RULES_INFRACTION, "Administrative forfeit due to losing player's failure to observe either the Laws of Chess or the event regulations."),
        (TIME_FORFEIT, "Loss due to losing player's failure to meet time control requirements."),
        (UNTERMINATED, "Game not terminated."),
    ]

    result = TextField(
        choices=RESULT_CHOICES,
        default=IN_PROGRESS,
    )
    termination = TextField(
        choices=TERMINATION_CHOICES,
        default=UNTERMINATED,
    )

    def __str__(self):
        return self.result


class Board(Model):
    BLACK_PIECES = ['q', 'k', 'b', 'n', 'r', 'p']
    WHITE_PIECES = [p.upper() for p in BLACK_PIECES]

    fen = TextField(
        default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    ep_square = CharField(max_length=2, null=True)
    castling_xfen = TextField(null=True)
    castling_rights = TextField(null=True)
    turn = IntegerField(null=True)
    fullmove_number = IntegerField(default=1)
    halfmove_clock = IntegerField(default=0)

    updated_at = DateTimeField(auto_now=True)
    game_uuid = UUIDField(default=uuid.uuid4)

    def __str__(self):
        return self.fen

    @classmethod
    def from_fen(cls, fen):
        """
        A FEN string contains the position part board_fen(), the turn, the castling part (castling_rights), 
        the en passant square (ep_square), the halfmove_clock and the fullmove_number.
        """

        board = chess.Board(fen)

        board_data = {
            "fen": board.fen(),
            "turn": board.turn,
            "castling_xfen": board.castling_xfen(),
            "castling_rights": board.castling_rights,
            "ep_square": board.ep_square,
            "fullmove_number": board.fullmove_number,
            "halfmove_clock": board.halfmove_clock,
        }
        
        return cls(**board_data)

                
class Piece(Model):
    BLACK_PAWN_SYMBOL = "P"
    BLACK_KNIGHT_SYMBOL = "N"
    BLACK_BISHOP_SYMBOL = "B"
    BLACK_ROOK_SYMBOL = "R"
    BLACK_QUEEN_SYMBOL = "Q"
    BLACK_KING_SYMBOL = "K"
    WHITE_PAWN_SYMBOL = "p"
    WHITE_KNIGHT_SYMBOL = "n"
    WHITE_BISHOP_SYMBOL = "b"
    WHITE_ROOK_SYMBOL = "r"
    WHITE_QUEEN_SYMBOL = "q"
    WHITE_KING_SYMBOL = "k"

    PIECE_CHOICES = [
        (BLACK_PAWN_SYMBOL, "Black pawn"),
        (BLACK_KNIGHT_SYMBOL, "Black knight"),
        (BLACK_BISHOP_SYMBOL, "Black bishop"),
        (BLACK_ROOK_SYMBOL, "Black rook"),
        (BLACK_QUEEN_SYMBOL, "Black queen"),
        (BLACK_KING_SYMBOL, "Black king"),
        (WHITE_PAWN_SYMBOL, "White pawn"),
        (WHITE_KNIGHT_SYMBOL, "White knight"),
        (WHITE_BISHOP_SYMBOL, "White bishop"),
        (WHITE_ROOK_SYMBOL, "White rook"),
        (WHITE_QUEEN_SYMBOL, "White queen"),
        (WHITE_KING_SYMBOL, "White king"),
    ]

    SQUARE_CHOICES = [(getattr(chess, i.upper()), i.upper(),) for i in chess.SQUARE_NAMES]
    
    piece_type = CharField(
        max_length=1,
        choices=PIECE_CHOICES,
    )
    
    square = CharField(
        max_length=2,
        choices=SQUARE_CHOICES,
        null=True,
    )

    captured = BooleanField(default=False)
    board = ForeignKey(
        Board,
        on_delete=CASCADE,
    )

    def __str__(self):
        return self.piece_type

    @classmethod
    def get_all_pieces(cls, fen):
        """
        Return a list of Piece instances from a fen string
        """
        
        board = chess.Board(fen)
        
        

class Game(Model):
    uuid = UUIDField(default=uuid.uuid4, primary_key=True)
    whites_player = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='whites_player',
        null=True,
    )
    blacks_player = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='blacks_player',
        null=True,
    )
    created_at = DateTimeField(auto_now_add=True)
    started_at = DateTimeField(null=True)
    finished_at = DateTimeField(null=True)
    result = OneToOneField(
        Result,
        on_delete=CASCADE,
    )
    board = OneToOneField(
        Board,
        on_delete=CASCADE,
    )


class Move(Model):
    """
    Each individual move that composes a board's move stack
    """
    
    timestamp = DateTimeField(auto_now_add=True)
    piece = ForeignKey(
        Piece,
        on_delete=CASCADE,
    )
    from_square = TextField()
    to_square = TextField()

    def __str__(self):
        return f'{from_square}{to_square}'


class Position(Model):
    piece_file = CharField(max_length=1)
    piece_rank = CharField(max_length=1)
    timestamp = DateTimeField(auto_now_add=True)
    uuid = UUIDField(default=uuid.uuid4)
    piece = ForeignKey(
        Piece,
        on_delete=CASCADE,
    )

    def __str__(self):
        return f'{piece_file}{piece_rank}'


class Claim(Model):
    THREEFOLD_REPETITION = 'tr'
    FIFTY_MOVES = 'ft'
    DRAW = 'd'

    CLAIM_CHOICES = [
        (THREEFOLD_REPETITION, 'Threefold repetition'),
        (FIFTY_MOVES, 'Fifty moves'),
        (DRAW, 'Draw'),
    ]

    claim_type = CharField(
        max_length=2,
        choices=CLAIM_CHOICES,
    )

    def __str__(self):
        return self.claim_type


class ClaimItem(Model):
    player = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
    )
    timestamp = DateTimeField(auto_now_add=True)
    claim = ForeignKey(
        Claim,
        on_delete=CASCADE,
    )
