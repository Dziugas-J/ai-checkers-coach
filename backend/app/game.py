from app.board import CreateBoard
from app.models import GameState

def CreateNewGame() -> GameState:
    return GameState(
        board=CreateBoard(),
        current_player="white",
        winner=None,
        must_continue_capture=False,
        forced_piece=None,
    )

def IsForcedCapturePiece(game: GameState, row: int, col: int) -> bool:
    if not game.must_continue_capture:
        return True
    if game.forced_piece is None:
        return False
    if game.forced_piece.row == row and game.forced_piece.col == col:
        return True
    return False