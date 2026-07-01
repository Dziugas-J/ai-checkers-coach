import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.game_logic.round import (
    accept_bot_draw,
    apply_bot_move,
    apply_player_move_to_round,
    create_new_round,
    decline_bot_draw,
    finish_bot_surrender,
    get_player_hint,
    get_player_legal_moves,
    player_offer_draw_to_bot,
)
from app.game_logic.models import (
    PlayerHintRequest,
    HintResponse,
    LegalMove,
    BotMoveRequest,
    PlayerDrawRequest,
    PlayerLegalMovesRequest,
    PlayerMoveRequest,
    RoundState,
    FinishBotSurrenderRequest,
    NewRoundRequest,
)

app = FastAPI(title="Checkers", version="0.1.0")

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        frontend_url,
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/round/new")
def new_round(request: NewRoundRequest) -> RoundState:
    return create_new_round(request.difficulty)

@app.post("/round/legal-moves")
def player_legal_moves(request: PlayerLegalMovesRequest) -> list[LegalMove]:
    return get_player_legal_moves(
        request.round,
        request.row,
        request.col,
    )

@app.post("/round/move")
def player_move(request: PlayerMoveRequest) -> RoundState:
    return apply_player_move_to_round(
        request.round,
        request.start_row,
        request.start_col,
        request.target_row,
        request.target_col,
    )

@app.post("/round/hint")
def player_hint(request: PlayerHintRequest) -> HintResponse:
    return get_player_hint(request.round)

@app.post("/round/bot-move")
def bot_move(request: BotMoveRequest) -> RoundState:
    return apply_bot_move(request.round)

@app.post("/round/draw/accept")
def accept_round_draw(request: PlayerDrawRequest) -> RoundState:
    return accept_bot_draw(request.round)

@app.post("/round/draw/decline")
def decline_round_draw(request: PlayerDrawRequest) -> RoundState:
    return decline_bot_draw(request.round)

@app.post("/round/draw/offer")
def player_draw_offer(request: PlayerDrawRequest) -> RoundState:
    return player_offer_draw_to_bot(request.round)

@app.post("/round/surrender/finish")
def finish_round_surrender(request: FinishBotSurrenderRequest) -> RoundState:
    return finish_bot_surrender(request.round)