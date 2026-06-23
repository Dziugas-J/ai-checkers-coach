from typing import Literal, TypeAlias

Piece: TypeAlias = Literal["empty", "red", "black"]
Board: TypeAlias = list[list[Piece]]