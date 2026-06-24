from typing import Literal, TypeAlias
from pydantic import BaseModel


Piece: TypeAlias = Literal["empty", "red", "black"]
Player: TypeAlias = Literal["red", "black"]
Board: TypeAlias = list[list[Piece]]


class GameState(BaseModel):
    board: Board
    current_player: Player
    winner: Player | None = None
    message: str