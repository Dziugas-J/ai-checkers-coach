import random

from app.game_logic.models import Board, Difficulty, GameState, Player
from app.game_logic.pieces import get_next_player, get_piece_owner

def count_player_pieces(board: Board, player: Player) -> int:
    count = 0

    for row in board:
        for piece in row:
            if get_piece_owner(piece) == player:
                count += 1

    return count

def get_piece_value(piece: str) -> int:
    if piece == "white" or piece == "black":
        return 1

    if piece == "white_king" or piece == "black_king":
        return 2

    return 0

def get_player_material_score(board: Board, player: Player) -> int:
    score = 0

    for row in board:
        for piece in row:
            if get_piece_owner(piece) == player:
                score += get_piece_value(piece)

    return score

def get_bot_material_advantage(game: GameState) -> int:
    white_score = get_player_material_score(game.board, "white")
    black_score = get_player_material_score(game.board, "black")

    return black_score - white_score

def get_bot_material_deficit(game: GameState) -> int:
    bot_advantage = get_bot_material_advantage(game)

    if bot_advantage >= 0:
        return 0

    return abs(bot_advantage)

def should_bot_accept_player_draw(game: GameState, difficulty: Difficulty) -> bool:
    accept_chance = get_bot_draw_offer(game, difficulty)

    if accept_chance <= 0:
        return False
    if accept_chance >= 100:
        return True

    roll = random.randint(1, 100)
    return roll <= accept_chance

def get_deficit_draw_chance(deficit: int, difficulty: Difficulty) -> int:
    if difficulty == "easy":
        if deficit >= 5:
            return 80
        if deficit == 4:
            return 65
        if deficit == 3:
            return 50
        if deficit == 2:
            return 25
        return 0

    if difficulty == "medium":
        if deficit >= 6:
            return 75
        if deficit == 5:
            return 65
        if deficit == 4:
            return 50
        if deficit == 3:
            return 30
        if deficit == 2:
            return 10
        return 0

    if deficit >= 7:
        return 65
    if deficit == 6:
        return 55
    if deficit == 5:
        return 40
    if deficit == 4:
        return 25
    if deficit == 3:
        return 10
    return 0

def get_one_piece_endgame_draw_chance(
    white_pieces: int,
    black_pieces: int,
    difficulty: Difficulty,
) -> int:
    if black_pieces != 1:
        return 0

    if white_pieces >= 5:
        return 0
    
    if white_pieces == 4:
        if difficulty == "easy":
            return 75
        if difficulty == "medium":
            return 60
        return 45
    
    if white_pieces == 3:
        if difficulty == "easy":
            return 60
        if difficulty == "medium":
            return 45
        return 25
    
    if white_pieces == 2:
        if difficulty == "easy":
            return 35
        if difficulty == "medium":
            return 25
        return 10
    return 0

def get_bot_draw_offer(game: GameState, difficulty: Difficulty) -> int:
    deficit = get_bot_material_deficit(game)
    white_pieces = count_player_pieces(game.board, "white")
    black_pieces = count_player_pieces(game.board, "black")

    deficit_chance = get_deficit_draw_chance(deficit, difficulty)

    endgame_chance = get_one_piece_endgame_draw_chance(
        white_pieces,
        black_pieces,
        difficulty,
    )
    return max(deficit_chance, endgame_chance)

def bot_should_offer_draw(game: GameState, difficulty: Difficulty) -> bool:
    draw_chance = get_bot_draw_offer(game, difficulty)

    if draw_chance <= 0:
        return False
    if draw_chance >= 100:
        return True

    roll = random.randint(1, 100)
    return roll <= draw_chance

def get_winner(
    game: GameState,
    current_player_can_move: bool,
) -> Player | None:
    white_pieces = count_player_pieces(game.board, "white")
    black_pieces = count_player_pieces(game.board, "black")

    if white_pieces == 0:
        return "black"
    if black_pieces == 0:
        return "white"
    if not current_player_can_move:
        return get_next_player(game.current_player)
    return None


def add_winner_if_game_finished(
    game: GameState,
    current_player_can_move: bool,
) -> GameState:
    winner = get_winner(
        game,
        current_player_can_move,
    )

    if winner is None:
        return game
    return GameState(
        board=game.board,
        current_player=game.current_player,
        winner=winner,
        must_continue_capture=False,
        forced_piece=None,
    )

def bot_should_give_up(game: GameState) -> bool:
    white_pieces = count_player_pieces(game.board, "white")
    black_pieces = count_player_pieces(game.board, "black")
    
    if black_pieces == 1 and white_pieces >= 5:
        return True
    return False