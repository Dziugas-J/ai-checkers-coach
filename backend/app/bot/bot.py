import random
from typing import TypeAlias

from app.game_logic.models import Difficulty, GameState, LegalMove
from app.game_logic.moves import apply_move, get_legal_moves

MoveOption: TypeAlias = tuple[int, int, int, int, LegalMove]

def get_all_current_player_moves(game: GameState) -> list[MoveOption]:
    all_moves = []

    for row in range(len(game.board)):
        for col in range(len(game.board[row])):
            legal_moves = get_legal_moves(game, row, col)

            for move in legal_moves:
                all_moves.append(
                    (
                        row,
                        col,
                        move.row,
                        move.col,
                        move,
                    )
                )

    return all_moves


def apply_move_option(game: GameState, move_option: MoveOption) -> GameState:
    start_row = move_option[0]
    start_col = move_option[1]
    target_row = move_option[2]
    target_col = move_option[3]

    return apply_move(
        game,
        start_row,
        start_col,
        target_row,
        target_col,
    )


def score_bot_move(game: GameState, move_option: MoveOption) -> int:
    start_row = move_option[0]
    target_row = move_option[2]
    legal_move = move_option[4]

    piece = game.board[start_row][move_option[1]]
    score = 0

    if legal_move.is_capture:
        score += 10

    if piece == "black" and target_row == 7:
        score += 8

    if piece == "black_king":
        score += 3

    if piece == "black" and target_row > start_row:
        score += 1

    return score


def evaluate_board_for_bot(game: GameState) -> int:
    score = 0

    for row in game.board:
        for piece in row:
            if piece == "black":
                score += 3
            elif piece == "black_king":
                score += 5
            elif piece == "white":
                score -= 3
            elif piece == "white_king":
                score -= 5

    return score


def choose_easy_move(move_options: list[MoveOption]) -> MoveOption:
    return random.choice(move_options)


def choose_medium_move(game: GameState, move_options: list[MoveOption]) -> MoveOption:
    best_score = None
    best_moves = []

    for move_option in move_options:
        move_score = score_bot_move(game, move_option)

        if best_score is None or move_score > best_score:
            best_score = move_score
            best_moves = [move_option]
        elif move_score == best_score:
            best_moves.append(move_option)

    return random.choice(best_moves)


def choose_hard_move(game: GameState, move_options: list[MoveOption]) -> MoveOption:
    best_score = None
    best_moves = []

    for move_option in move_options:
        game_after_black_move = apply_move_option(game, move_option)
        move_score = evaluate_board_for_bot(game_after_black_move)

        if game_after_black_move.current_player == "white":
            white_moves = get_all_current_player_moves(game_after_black_move)

            if len(white_moves) == 0:
                move_score = 999
            else:
                worst_score_after_white_reply = None

                for white_move in white_moves:
                    game_after_white_move = apply_move_option(
                        game_after_black_move,
                        white_move,
                    )

                    reply_score = evaluate_board_for_bot(game_after_white_move)

                    if (
                        worst_score_after_white_reply is None
                        or reply_score < worst_score_after_white_reply
                    ):
                        worst_score_after_white_reply = reply_score

                move_score = worst_score_after_white_reply

        if best_score is None or move_score > best_score:
            best_score = move_score
            best_moves = [move_option]
        elif move_score == best_score:
            best_moves.append(move_option)

    return random.choice(best_moves)


def choose_bot_move(
    game: GameState,
    move_options: list[MoveOption],
    difficulty: Difficulty,
) -> MoveOption:
    if difficulty == "easy":
        return choose_easy_move(move_options)

    if difficulty == "medium":
        return choose_medium_move(game, move_options)

    return choose_hard_move(game, move_options)


def apply_bot_move(game: GameState, difficulty: Difficulty) -> GameState:
    if game.current_player != "black":
        return game

    move_options = get_all_current_player_moves(game)

    if len(move_options) == 0:
        return GameState(
            board=game.board,
            current_player=game.current_player,
            winner="white",
            must_continue_capture=False,
            forced_piece=None,
        )

    selected_move = choose_bot_move(
        game,
        move_options,
        difficulty,
    )

    return apply_move_option(game, selected_move)