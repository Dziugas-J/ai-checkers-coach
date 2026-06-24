from typing import Literal, TypeAlias
from pydantic import BaseModel


Piece: TypeAlias = Literal["empty", "white", "black", "white_king", "black_king"]
Player: TypeAlias = Literal["white", "black"]
Board: TypeAlias = list[list[Piece]]


class GameState(BaseModel):
    board: Board
    current_player: Player
    winner: Player | None = None
    message: str