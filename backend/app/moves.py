from app.board import BOARD_SIZE, CopyBoard, IsInsideBoard
from app.game import IsForcedCapturePiece
from app.models import Board, GameState, LegalMove, Player, Position
from app.pieces import (
    GetCaptureDirections,
    GetNextPlayer,
    GetNormalMoveDirections,
    GetOpponent,
    GetPiecePlayer,
    IsKing,
    PromotePieceIfNeeded,
)

def GetPossibleMoves(board: Board, row: int, col: int) -> list[LegalMove]:
    piece = board[row][col]
    if not IsInsideBoard(row, col):
        return []
    elif piece == "empty":
        return []
    elif IsKing(piece):
        return GetKingPossibleMoves(board, row, col)
    else:
        return GetRegularPiecePossibleMoves(board, row, col)

def GetRegularPiecePossibleMoves(board: Board, row: int, col: int) -> list[LegalMove]:
    piece = board[row][col]
    opponent = GetOpponent(piece)

    normal_moves = []
    capture_moves = []

    move_directions = GetNormalMoveDirections(piece)

    for row_direction, col_direction in move_directions:
        target_row = row + row_direction
        target_col = col + col_direction

        if IsInsideBoard(target_row, target_col):
            if board[target_row][target_col] == "empty":
                normal_moves.append(
                    LegalMove(
                        row=target_row,
                        col=target_col,
                        is_capture=False,
                        captured_piece=None,
                    )
                )

    capture_directions = GetCaptureDirections()

    for row_direction, col_direction in capture_directions:
        middle_row = row + row_direction
        middle_col = col + col_direction
        target_row = row + row_direction * 2
        target_col = col + col_direction * 2

        if not IsInsideBoard(target_row, target_col):
            continue

        middle_piece = board[middle_row][middle_col]
        destination_piece = board[target_row][target_col]

        if GetPiecePlayer(middle_piece) == opponent:
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

def GetKingPossibleMoves(board: Board, row: int, col: int) -> list[LegalMove]:
    piece = board[row][col]
    piece_player = GetPiecePlayer(piece)
    opponent = GetOpponent(piece)

    normal_moves = []
    capture_moves = []

    directions = GetCaptureDirections()

    for row_direction, col_direction in directions:
        current_row = row + row_direction
        current_col = col + col_direction
        found_enemy = None

        while IsInsideBoard(current_row, current_col):
            current_piece = board[current_row][current_col]
            current_piece_player = GetPiecePlayer(current_piece)

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

def GetCaptureMoves(board: Board, row: int, col: int) -> list[LegalMove]:
    possible_moves = GetPossibleMoves(board, row, col)
    capture_moves = []

    for move in possible_moves:
        if move.is_capture:
            capture_moves.append(move)

    return capture_moves

def PlayerHasCapture(board: Board, player: Player) -> bool:
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]

            if GetPiecePlayer(piece) != player:
                continue

            capture_moves = GetCaptureMoves(board, row, col)

            if len(capture_moves) > 0:
                return True

    return False

def FindLegalMove(
    board: Board,
    player: Player,
    start_row: int,
    start_col: int,
    target_row: int,
    target_col: int,
) -> LegalMove | None:
    if not IsInsideBoard(start_row, start_col):
        return None

    if not IsInsideBoard(target_row, target_col):
        return None

    piece = board[start_row][start_col]

    if GetPiecePlayer(piece) != player:
        return None

    possible_moves = GetPossibleMoves(board, start_row, start_col)
    player_must_capture = PlayerHasCapture(board, player)

    for move in possible_moves:
        if move.row == target_row and move.col == target_col:
            if player_must_capture and not move.is_capture:
                return None

            return move

    return None

def GetLegalMovesForGame(
    game: GameState,
    row: int,
    col: int,
) -> list[LegalMove]:
    if not IsInsideBoard(row, col):
        return []

    piece = game.board[row][col]

    if GetPiecePlayer(piece) != game.current_player:
        return []

    if game.must_continue_capture:
        if game.forced_piece is None:
            return []

        if game.forced_piece.row != row or game.forced_piece.col != col:
            return []

        return GetCaptureMoves(game.board, row, col)

    possible_moves = GetPossibleMoves(game.board, row, col)
    capture_moves = []

    for move in possible_moves:
        if move.is_capture:
            capture_moves.append(move)

    if PlayerHasCapture(game.board, game.current_player):
        return capture_moves

    return possible_moves

def ApplyMoveToGame(
    game: GameState,
    start_row: int,
    start_col: int,
    target_row: int,
    target_col: int,
) -> GameState:
    if game.winner is not None:
        return game

    if not IsForcedCapturePiece(game, start_row, start_col):
        return game

    legal_move = FindLegalMove(
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

    new_board = CopyBoard(game.board)

    moving_piece = new_board[start_row][start_col]
    new_board[start_row][start_col] = "empty"

    promoted_piece = PromotePieceIfNeeded(moving_piece, target_row)
    new_board[target_row][target_col] = promoted_piece

    if legal_move.is_capture and legal_move.captured_piece is not None:
        captured_row = legal_move.captured_piece.row
        captured_col = legal_move.captured_piece.col
        new_board[captured_row][captured_col] = "empty"

    if legal_move.is_capture:
        next_capture_moves = GetCaptureMoves(new_board, target_row, target_col)

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

    return GameState(
        board=new_board,
        current_player=GetNextPlayer(game.current_player),
        winner=game.winner,
        must_continue_capture=False,
        forced_piece=None,
    )