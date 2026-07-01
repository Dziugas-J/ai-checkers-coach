from app.game_logic.board import BOARD_SIZE, copy_board, is_position_in_board
from app.game_logic.game import can_move_piece
from app.game_logic.models import Board, GameState, LegalMove, Player, Position
from app.game_logic.pieces import (
    get_diagonal_directions,
    get_next_player,
    get_legal_move_directions,
    get_opponent_player,
    get_piece_owner,
    is_piece_king,
    promote_piece,
)
from app.game_logic.winner import add_winner_if_game_finished


def get_possible_moves(board: Board, row: int, col: int) -> list[LegalMove]:
    if not is_position_in_board(row, col):
        return []

    piece = board[row][col]

    if piece == "empty":
        return []

    if is_piece_king(piece):
        return get_king_moves(board, row, col)

    return get_regular_piece_moves(board, row, col)


def get_regular_piece_moves(board: Board, row: int, col: int) -> list[LegalMove]:
    piece = board[row][col]
    opponent = get_opponent_player(piece)

    normal_moves = []
    capture_moves = []

    move_directions = get_legal_move_directions(piece)

    for row_direction, col_direction in move_directions:
        target_row = row + row_direction
        target_col = col + col_direction

        if is_position_in_board(target_row, target_col):
            if board[target_row][target_col] == "empty":
                normal_moves.append(
                    LegalMove(
                        row=target_row,
                        col=target_col,
                        is_capture=False,
                        captured_piece=None,
                    )
                )

    capture_directions = get_diagonal_directions()

    for row_direction, col_direction in capture_directions:
        middle_row = row + row_direction
        middle_col = col + col_direction
        target_row = row + row_direction * 2
        target_col = col + col_direction * 2

        if not is_position_in_board(target_row, target_col):
            continue

        middle_piece = board[middle_row][middle_col]
        destination_piece = board[target_row][target_col]

        if get_piece_owner(middle_piece) == opponent:
            if destination_piece == "empty":
                capture_moves.append(
                    LegalMove(
                        row=target_row,
                        col=target_col,
                        is_capture=True,
                        captured_piece=Position(
                            row=middle_row,
                            col=middle_col,
                        ),
                    )
                )

    if len(capture_moves) > 0:
        return capture_moves

    return normal_moves


def get_king_moves(board: Board, row: int, col: int) -> list[LegalMove]:
    piece = board[row][col]
    piece_player = get_piece_owner(piece)
    opponent = get_opponent_player(piece)

    normal_moves = []
    capture_moves = []

    directions = get_diagonal_directions()

    for row_direction, col_direction in directions:
        current_row = row + row_direction
        current_col = col + col_direction
        found_enemy = None

        while is_position_in_board(current_row, current_col):
            current_piece = board[current_row][current_col]
            current_piece_player = get_piece_owner(current_piece)

            if current_piece == "empty":
                if found_enemy is None:
                    normal_moves.append(
                        LegalMove(
                            row=current_row,
                            col=current_col,
                            is_capture=False,
                            captured_piece=None,
                        )
                    )
                else:
                    capture_moves.append(
                        LegalMove(
                            row=current_row,
                            col=current_col,
                            is_capture=True,
                            captured_piece=found_enemy,
                        )
                    )

                current_row = current_row + row_direction
                current_col = current_col + col_direction
                continue

            elif current_piece_player == piece_player:
                break

            elif current_piece_player == opponent:
                if found_enemy is not None:
                    break

                found_enemy = Position(
                    row=current_row,
                    col=current_col,
                )

                current_row = current_row + row_direction
                current_col = current_col + col_direction
                continue

            break

    if len(capture_moves) > 0:
        return capture_moves

    return normal_moves


def get_capture_moves(board: Board, row: int, col: int) -> list[LegalMove]:
    possible_moves = get_possible_moves(board, row, col)
    capture_moves = []

    for move in possible_moves:
        if move.is_capture:
            capture_moves.append(move)

    return capture_moves


def can_player_capture(board: Board, player: Player) -> bool:
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]

            if get_piece_owner(piece) != player:
                continue

            capture_moves = get_capture_moves(board, row, col)

            if len(capture_moves) > 0:
                return True

    return False


def find_legal_moves(
    board: Board,
    player: Player,
    start_row: int,
    start_col: int,
    target_row: int,
    target_col: int,
) -> LegalMove | None:
    if not is_position_in_board(start_row, start_col):
        return None

    if not is_position_in_board(target_row, target_col):
        return None

    piece = board[start_row][start_col]

    if get_piece_owner(piece) != player:
        return None

    possible_moves = get_possible_moves(board, start_row, start_col)
    player_must_capture = can_player_capture(board, player)

    for move in possible_moves:
        if move.row == target_row and move.col == target_col:
            if player_must_capture and not move.is_capture:
                return None

            return move

    return None


def get_legal_moves(
    game: GameState,
    row: int,
    col: int,
) -> list[LegalMove]:
    if not is_position_in_board(row, col):
        return []

    piece = game.board[row][col]

    if get_piece_owner(piece) != game.current_player:
        return []

    if game.must_continue_capture:
        if game.forced_piece is None:
            return []

        if game.forced_piece.row != row or game.forced_piece.col != col:
            return []

        return get_capture_moves(game.board, row, col)

    possible_moves = get_possible_moves(game.board, row, col)
    capture_moves = []

    for move in possible_moves:
        if move.is_capture:
            capture_moves.append(move)

    if can_player_capture(game.board, game.current_player):
        return capture_moves

    return possible_moves


def can_player_move(game: GameState, player: Player) -> bool:
    test_game = GameState(
        board=game.board,
        current_player=player,
        winner=game.winner,
        must_continue_capture=False,
        forced_piece=None,
    )

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = game.board[row][col]

            if get_piece_owner(piece) != player:
                continue

            legal_moves = get_legal_moves(test_game, row, col)

            if len(legal_moves) > 0:
                return True

    return False


def apply_move(
    game: GameState,
    start_row: int,
    start_col: int,
    target_row: int,
    target_col: int,
) -> GameState:
    if game.winner is not None:
        return game

    if not can_move_piece(game, start_row, start_col):
        return game

    legal_move = find_legal_moves(
        game.board,
        game.current_player,
        start_row,
        start_col,
        target_row,
        target_col,
    )

    if legal_move is None:
        return game

    if game.must_continue_capture and not legal_move.is_capture:
        return game

    new_board = copy_board(game.board)

    moving_piece = new_board[start_row][start_col]
    new_board[start_row][start_col] = "empty"

    promoted_piece = promote_piece(moving_piece, target_row)
    new_board[target_row][target_col] = promoted_piece

    if legal_move.is_capture and legal_move.captured_piece is not None:
        captured_row = legal_move.captured_piece.row
        captured_col = legal_move.captured_piece.col
        new_board[captured_row][captured_col] = "empty"

    if legal_move.is_capture:
        next_capture_moves = get_capture_moves(new_board, target_row, target_col)

        if len(next_capture_moves) > 0:
            return GameState(
                board=new_board,
                current_player=game.current_player,
                winner=game.winner,
                must_continue_capture=True,
                forced_piece=Position(
                    row=target_row,
                    col=target_col,
                ),
            )

    updated_game = GameState(
        board=new_board,
        current_player=get_next_player(game.current_player),
        winner=game.winner,
        must_continue_capture=False,
        forced_piece=None,
    )

    current_player_can_move = can_player_move(
        updated_game,
        updated_game.current_player,
    )

    return add_winner_if_game_finished(
        updated_game,
        current_player_can_move,
    )