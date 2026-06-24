from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.game_logic import CreateBoard, CreateNewGame
from app.models import Board, GameState

app = FastAPI(
    title="AI Checkers Coach",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/checkers")
def test_board() -> dict[str, Board]:
    return {
        "board": CreateBoard(),
    }

@app.post("/game/new")
def new_game() -> GameState:
    return CreateNewGame()