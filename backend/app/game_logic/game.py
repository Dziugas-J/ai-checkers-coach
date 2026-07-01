from app.game_logic.board import create_board
from app.game_logic.models import GameState

def create_new_game() -> GameState:
    return GameState(
        board=create_board(),
        current_player="white",
        winner=None,
        must_continue_capture=False,
        forced_piece=None,
    )

def can_move_piece(game: GameState, row: int, col: int) -> bool:
    if not game.must_continue_capture:
        return True
    if game.forced_piece is None:
        return False
    if game.forced_piece.row == row and game.forced_piece.col == col:
        return True
    return False