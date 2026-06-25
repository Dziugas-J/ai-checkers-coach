from typing import Literal, TypeAlias

from pydantic import BaseModel

Piece: TypeAlias = Literal[
    "empty",
    "white",
    "black",
    "white_king",
    "black_king",
]

Player: TypeAlias = Literal["white", "black"]
Board: TypeAlias = list[list[Piece]]

class Position(BaseModel):
    row: int
    col: int

class LegalMove(BaseModel):
    row: int
    col: int
    is_capture: bool
    captured_piece: Position | None = None

class GameState(BaseModel):
    board: Board
    current_player: Player
    winner: Player | None = None
    must_continue_capture: bool = False
    forced_piece: Position | None = None

class MoveRequest(BaseModel):
    game: GameState
    start_row: int
    start_col: int
    target_row: int
    target_col: int

class LegalMovesRequest(BaseModel):
    game: GameState
    row: int
    col: int