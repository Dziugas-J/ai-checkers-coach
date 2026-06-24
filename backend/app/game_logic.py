from app.models import Board, GameState

BOARD_SIZE = 8

def create_board() -> Board:
    board = []

    for row in range(BOARD_SIZE):
        current_row = []

        for col in range(BOARD_SIZE):
            dark_square = (row + col) % 2 == 1
            
            if dark_square and row < 3:
                current_row.append("black")
            elif dark_square and row > 4:
                current_row.append("red")
            else:
                current_row.append("empty")
        board.append(current_row)
    return board

def create_new_game() -> GameState:
    return GameState(
        board=create_board(),
        current_player="red",
        winner=None,
        message="New game created",
    )