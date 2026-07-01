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
Difficulty: TypeAlias = Literal["easy", "medium", "hard"]
DrawOfferBy: TypeAlias = Literal["white", "black"]

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

class RoundState(BaseModel):
    game: GameState
    difficulty: Difficulty
    player_score: int = 0
    computer_score: int = 0
    draw_offer_by: DrawOfferBy | None = None
    draw_offer_message: str | None = None
    turn_number: int = 0
    bot_draw_offer_count: int = 0
    last_bot_draw_offer_turn: int | None = None
    last_bot_draw_offer_deficit: int | None = None
    surrender_by: Player | None = None
    surrender_message: str | None = None

class NewRoundRequest(BaseModel):
    difficulty: Difficulty

class PlayerMoveRequest(BaseModel):
    round: RoundState
    start_row: int
    start_col: int
    target_row: int
    target_col: int

class PlayerLegalMovesRequest(BaseModel):
    round: RoundState
    row: int
    col: int

class PlayerDrawRequest(BaseModel):
    round: RoundState

class BotMoveRequest(BaseModel):
    round: RoundState

class FinishBotSurrenderRequest(BaseModel):
    round: RoundState

class PlayerHintRequest(BaseModel):
    round: RoundState

class HintResponse(BaseModel):
    hint: str
    start_row: int | None = None
    start_col: int | None = None
    target_row: int | None = None
    target_col: int | None = None
