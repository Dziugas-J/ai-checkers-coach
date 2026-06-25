from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.board import CreateBoard
from app.game import CreateNewGame
from app.models import Board, GameState, LegalMove, LegalMovesRequest, MoveRequest
from app.moves import ApplyMoveToGame, GetLegalMovesForGame

app = FastAPI(title="AI Checkers Coach", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/checkers")
def TestBoard() -> dict[str, Board]:
    return {"board": CreateBoard()}

@app.post("/game/new")
def NewGame() -> GameState:
    return CreateNewGame()

@app.post("/game/move")
def MakeMove(move_request: MoveRequest) -> GameState:
    return ApplyMoveToGame(
        move_request.game,
        move_request.start_row,
        move_request.start_col,
        move_request.target_row,
        move_request.target_col,
    )

@app.post("/game/legal-moves")
def GetLegalMoves(request: LegalMovesRequest) -> list[LegalMove]:
    return GetLegalMovesForGame(
        request.game,
        request.row,
        request.col,
    )