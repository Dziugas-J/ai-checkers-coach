from app.game_logic.models import Board


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
                current_row.append("white")
            else:
                current_row.append("empty")

        board.append(current_row)

    return board


def copy_board(board: Board) -> Board:
    return [row.copy() for row in board]


def is_position_in_board(row: int, col: int) -> bool:
    return row >= 0 and row < BOARD_SIZE and col >= 0 and col < BOARD_SIZE