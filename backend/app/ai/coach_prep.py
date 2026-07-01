from app.game_logic.board import BOARD_SIZE
from app.game_logic.models import GameState, LegalMove
from app.game_logic.moves import apply_move, get_legal_moves


def square_name(row: int, col: int) -> str:
    file_name = chr(ord("A") + col)
    rank = BOARD_SIZE - row

    return f"{file_name}{rank}"


def board_has_king(game: GameState) -> bool:
    for row in game.board:
        for piece in row:
            if piece == "white_king" or piece == "black_king":
                return True

    return False


def get_piece_name(piece: str) -> str:
    if piece == "white":
        return "white regular"

    if piece == "black":
        return "black regular"

    if piece == "white_king":
        return "white king"

    if piece == "black_king":
        return "black king"

    return "empty"


def get_piece_description(piece: str, row: int, col: int) -> str | None:
    square = square_name(row, col)

    if piece == "white":
        return f"{square} regular"

    if piece == "white_king":
        return f"{square} king"

    if piece == "black":
        return f"{square} regular"

    if piece == "black_king":
        return f"{square} king"

    return None


def get_position_text(game: GameState) -> str:
    white_pieces = []
    black_pieces = []

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = game.board[row][col]

            piece_description = get_piece_description(
                piece,
                row,
                col,
            )

            if piece_description is None:
                continue

            if piece == "white" or piece == "white_king":
                white_pieces.append(piece_description)

            if piece == "black" or piece == "black_king":
                black_pieces.append(piece_description)

    white_text = "\n".join(
        f"- {piece}"
        for piece in white_pieces
    )

    black_text = "\n".join(
        f"- {piece}"
        for piece in black_pieces
    )

    return (
        f"White pieces:\n{white_text}\n\n"
        f"Black pieces:\n{black_text}"
    )


def move_promotes_to_king(piece: str, target_row: int) -> bool:
    if piece == "white" and target_row == 0:
        return True

    if piece == "black" and target_row == 7:
        return True

    return False


def move_to_text(
    game: GameState,
    start_row: int,
    start_col: int,
    move: LegalMove,
) -> str:
    piece = game.board[start_row][start_col]

    start_square = square_name(start_row, start_col)
    target_square = square_name(move.row, move.col)

    move_text = f"{start_square} -> {target_square}"

    details = []

    if move.is_capture and move.captured_piece is not None:
        captured_square = square_name(
            move.captured_piece.row,
            move.captured_piece.col,
        )

        details.append(f"captures on {captured_square}")

    if move_promotes_to_king(piece, move.row):
        details.append("promotes to king")

    piece_name = get_piece_name(piece)

    if len(details) > 0:
        return f"{move_text} ({piece_name}, {', '.join(details)})"

    return f"{move_text} ({piece_name})"


def get_all_current_player_move_options(
    game: GameState,
) -> list[tuple[int, int, LegalMove]]:
    move_options = []

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            moves = get_legal_moves(game, row, col)

            for move in moves:
                move_options.append(
                    (
                        row,
                        col,
                        move,
                    )
                )

    return move_options


def get_max_capture_sequence_length(game: GameState, depth: int = 0) -> int:
    if depth >= 12:
        return 0

    move_options = get_all_current_player_move_options(game)

    best_capture_count = 0

    for start_row, start_col, move in move_options:
        if not move.is_capture:
            continue

        game_after_move = apply_move(
            game,
            start_row,
            start_col,
            move.row,
            move.col,
        )

        capture_count = 1

        if (
            game_after_move.current_player == game.current_player
            and game_after_move.must_continue_capture
        ):
            capture_count += get_max_capture_sequence_length(
                game_after_move,
                depth + 1,
            )

        if capture_count > best_capture_count:
            best_capture_count = capture_count

    return best_capture_count


def get_opponent_capture_danger_after_move(
    game: GameState,
    start_row: int,
    start_col: int,
    move: LegalMove,
) -> int:
    game_after_white_move = apply_move(
        game,
        start_row,
        start_col,
        move.row,
        move.col,
    )

    if game_after_white_move.winner is not None:
        return 0

    if game_after_white_move.current_player != "black":
        return 0

    return get_max_capture_sequence_length(game_after_white_move)


def get_move_safety_text(
    game: GameState,
    start_row: int,
    start_col: int,
    move: LegalMove,
) -> str:
    opponent_capture_count = get_opponent_capture_danger_after_move(
        game,
        start_row,
        start_col,
        move,
    )

    if opponent_capture_count <= 0:
        return "safe: black has no immediate capture"

    if opponent_capture_count == 1:
        return "warning: black can capture 1 piece"

    return f"danger: black can make a {opponent_capture_count}-capture sequence"


def move_to_coach_text(
    game: GameState,
    start_row: int,
    start_col: int,
    move: LegalMove,
) -> str:
    move_text = move_to_text(
        game,
        start_row,
        start_col,
        move,
    )

    safety_text = get_move_safety_text(
        game,
        start_row,
        start_col,
        move,
    )

    return f"{move_text} ({safety_text})"


def get_legal_moves_text(game: GameState) -> list[str]:
    safe_moves_text = []
    risky_moves_text = []
    capture_moves_text = []

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            moves = get_legal_moves(game, row, col)

            for move in moves:
                move_text = move_to_coach_text(
                    game,
                    row,
                    col,
                    move,
                )

                if move.is_capture:
                    capture_moves_text.append(move_text)
                    continue

                opponent_capture_count = get_opponent_capture_danger_after_move(
                    game,
                    row,
                    col,
                    move,
                )

                if opponent_capture_count == 0:
                    safe_moves_text.append(move_text)
                else:
                    risky_moves_text.append(move_text)

    if len(capture_moves_text) > 0:
        return capture_moves_text

    if len(safe_moves_text) > 0:
        return safe_moves_text

    return risky_moves_text


def legal_moves_include_promotion(legal_moves: list[str]) -> bool:
    for move in legal_moves:
        if "promotes to king" in move:
            return True

    return False