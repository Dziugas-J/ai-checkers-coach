from app.ai.coach import get_ai_hint
from app.bot.bot import apply_bot_move as apply_bot_move_to_game
from app.game_logic.game import create_new_game
from app.game_logic.models import (
    Difficulty,
    GameState,
    HintResponse,
    LegalMove,
    RoundState,
)
from app.game_logic.moves import apply_move, get_legal_moves
from app.game_logic.winner import (
    should_bot_accept_player_draw,
    bot_should_give_up,
    bot_should_offer_draw,
    get_bot_material_deficit,
)

BOT_DRAW_COOLDOWN_TURNS = {
    "easy": 6,
    "medium": 8,
    "hard": 10,
}

BOT_DRAW_MAX_OFFERS = {
    "easy": 3,
    "medium": 2,
    "hard": 2,
}

BOT_DRAW_WORSE_DEFICIT_STEP = 2

def create_new_round(difficulty: Difficulty) -> RoundState:
    return RoundState(
        game=create_new_game(),
        difficulty=difficulty,
        player_score=0,
        computer_score=0,
        draw_offer_by=None,
        draw_offer_message=None,
        turn_number=0,
        bot_draw_offer_count=0,
        last_bot_draw_offer_turn=None,
        last_bot_draw_offer_deficit=None,
        surrender_by=None,
        surrender_message=None,
    )


def create_route_with_game(round: RoundState, game: GameState) -> RoundState:
    return RoundState(
        game=game,
        difficulty=round.difficulty,
        player_score=round.player_score,
        computer_score=round.computer_score,
        draw_offer_by=round.draw_offer_by,
        draw_offer_message=round.draw_offer_message,
        turn_number=round.turn_number,
        bot_draw_offer_count=round.bot_draw_offer_count,
        last_bot_draw_offer_turn=round.last_bot_draw_offer_turn,
        last_bot_draw_offer_deficit=round.last_bot_draw_offer_deficit,
        surrender_by=round.surrender_by,
        surrender_message=round.surrender_message,
    )


def create_round_with_draw_message(
    round: RoundState,
    draw_offer_by: str | None,
    draw_offer_message: str | None,
) -> RoundState:
    return RoundState(
        game=round.game,
        difficulty=round.difficulty,
        player_score=round.player_score,
        computer_score=round.computer_score,
        draw_offer_by=draw_offer_by,
        draw_offer_message=draw_offer_message,
        turn_number=round.turn_number,
        bot_draw_offer_count=round.bot_draw_offer_count,
        last_bot_draw_offer_turn=round.last_bot_draw_offer_turn,
        last_bot_draw_offer_deficit=round.last_bot_draw_offer_deficit,
        surrender_by=round.surrender_by,
        surrender_message=round.surrender_message,
    )


def clear_draw_message(round: RoundState) -> RoundState:
    return create_round_with_draw_message(
        round,
        draw_offer_by=None,
        draw_offer_message=None,
    )


def increment_turn_number(round: RoundState) -> RoundState:
    return RoundState(
        game=round.game,
        difficulty=round.difficulty,
        player_score=round.player_score,
        computer_score=round.computer_score,
        draw_offer_by=round.draw_offer_by,
        draw_offer_message=round.draw_offer_message,
        turn_number=round.turn_number + 1,
        bot_draw_offer_count=round.bot_draw_offer_count,
        last_bot_draw_offer_turn=round.last_bot_draw_offer_turn,
        last_bot_draw_offer_deficit=round.last_bot_draw_offer_deficit,
        surrender_by=round.surrender_by,
        surrender_message=round.surrender_message,
    )


def add_score_if_game_finished(round: RoundState) -> RoundState:
    if round.game.winner is None:
        return round

    player_score = round.player_score
    computer_score = round.computer_score

    if round.game.winner == "white":
        player_score += 1

    if round.game.winner == "black":
        computer_score += 1

    return RoundState(
        game=create_new_game(),
        difficulty=round.difficulty,
        player_score=player_score,
        computer_score=computer_score,
        draw_offer_by=None,
        draw_offer_message=None,
        turn_number=0,
        bot_draw_offer_count=0,
        last_bot_draw_offer_turn=None,
        last_bot_draw_offer_deficit=None,
    )


def get_player_legal_moves(
    round: RoundState,
    row: int,
    col: int,
) -> list[LegalMove]:
    if round.draw_offer_by == "black":
        return []

    if round.surrender_by is not None:
        return []

    return get_legal_moves(
        round.game,
        row,
        col,
    )

def create_round_with_bot_surrender(round: RoundState) -> RoundState:
    return RoundState(
        game=round.game,
        difficulty=round.difficulty,
        player_score=round.player_score,
        computer_score=round.computer_score,
        draw_offer_by=None,
        draw_offer_message=None,
        turn_number=round.turn_number,
        bot_draw_offer_count=round.bot_draw_offer_count,
        last_bot_draw_offer_turn=round.last_bot_draw_offer_turn,
        last_bot_draw_offer_deficit=round.last_bot_draw_offer_deficit,
        surrender_by="black",
        surrender_message="Computer gives up. You win!",
    )


def apply_player_move_to_round(
    round: RoundState,
    start_row: int,
    start_col: int,
    target_row: int,
    target_col: int,
) -> RoundState:
    if round.game.current_player != "white":
        return round

    if round.draw_offer_by == "black":
        return round

    if round.surrender_by is not None:
        return round

    round = clear_draw_message(round)

    game_after_player_move = apply_move(
        round.game,
        start_row,
        start_col,
        target_row,
        target_col,
    )

    updated_round = create_route_with_game(
        round,
        game_after_player_move,
    )

    return add_score_if_game_finished(updated_round)


def get_player_hint(round: RoundState) -> HintResponse:
    if round.draw_offer_by == "black":
        return HintResponse(hint="Respond to the draw offer first.")

    if round.surrender_by is not None:
        return HintResponse(hint="Computer has given up.")

    if round.game.current_player == "white":
        for row in range(len(round.game.board)):
            for col in range(len(round.game.board[row])):
                moves = get_legal_moves(round.game, row, col)

                for move in moves:
                    if move.is_capture:
                        return HintResponse(
                            hint="You must take the forced capture.",
                            start_row=row,
                            start_col=col,
                            target_row=move.row,
                            target_col=move.col,
                        )

    return get_ai_hint(round.game)


def can_bot_offer_draw_now(round: RoundState) -> bool:
    max_offers = BOT_DRAW_MAX_OFFERS[round.difficulty]

    if round.bot_draw_offer_count >= max_offers:
        return False

    if round.last_bot_draw_offer_turn is None:
        return True

    current_deficit = get_bot_material_deficit(round.game)

    if round.last_bot_draw_offer_deficit is not None:
        deficit_got_much_worse = (
            current_deficit
            >= round.last_bot_draw_offer_deficit + BOT_DRAW_WORSE_DEFICIT_STEP
        )

        if deficit_got_much_worse:
            return True

    cooldown_turns = BOT_DRAW_COOLDOWN_TURNS[round.difficulty]
    turns_since_last_offer = round.turn_number - round.last_bot_draw_offer_turn

    return turns_since_last_offer >= cooldown_turns


def create_round_with_bot_draw_offer(round: RoundState) -> RoundState:
    return RoundState(
        game=round.game,
        difficulty=round.difficulty,
        player_score=round.player_score,
        computer_score=round.computer_score,
        draw_offer_by="black",
        draw_offer_message="Computer offers a draw.",
        turn_number=round.turn_number,
        bot_draw_offer_count=round.bot_draw_offer_count + 1,
        last_bot_draw_offer_turn=round.turn_number,
        last_bot_draw_offer_deficit=get_bot_material_deficit(round.game),
    )


def apply_bot_move(round: RoundState) -> RoundState:
    if round.game.current_player != "black":
        return round

    if round.game.winner is not None:
        return round

    if round.surrender_by is not None:
        return round

    game_after_bot_move = apply_bot_move_to_game(
        round.game,
        round.difficulty,
    )

    updated_round = create_route_with_game(
        round,
        game_after_bot_move,
    )

    if updated_round.game.current_player == "white":
        updated_round = increment_turn_number(updated_round)

    updated_round = add_score_if_game_finished(updated_round)

    if updated_round.game.current_player != "white":
        return updated_round

    if bot_should_give_up(updated_round.game):
        return create_round_with_bot_surrender(updated_round)

    if not can_bot_offer_draw_now(updated_round):
        return updated_round

    if bot_should_offer_draw(updated_round.game, updated_round.difficulty):
        return create_round_with_bot_draw_offer(updated_round)

    return updated_round

def finish_bot_surrender(round: RoundState) -> RoundState:
    if round.surrender_by != "black":
        return round

    return RoundState(
        game=create_new_game(),
        difficulty=round.difficulty,
        player_score=round.player_score + 1,
        computer_score=round.computer_score,
        draw_offer_by=None,
        draw_offer_message=None,
        turn_number=0,
        bot_draw_offer_count=0,
        last_bot_draw_offer_turn=None,
        last_bot_draw_offer_deficit=None,
        surrender_by=None,
        surrender_message=None,
    )

def accept_bot_draw(round: RoundState) -> RoundState:
    if round.draw_offer_by != "black":
        return round

    return RoundState(
        game=create_new_game(),
        difficulty=round.difficulty,
        player_score=round.player_score,
        computer_score=round.computer_score,
        draw_offer_by=None,
        draw_offer_message="Draw accepted. New game started.",
        turn_number=0,
        bot_draw_offer_count=0,
        last_bot_draw_offer_turn=None,
        last_bot_draw_offer_deficit=None,
    )


def decline_bot_draw(round: RoundState) -> RoundState:
    if round.draw_offer_by != "black":
        return round

    return RoundState(
        game=round.game,
        difficulty=round.difficulty,
        player_score=round.player_score,
        computer_score=round.computer_score,
        draw_offer_by=None,
        draw_offer_message="You declined the draw. Keep playing.",
        turn_number=round.turn_number,
        bot_draw_offer_count=round.bot_draw_offer_count,
        last_bot_draw_offer_turn=round.last_bot_draw_offer_turn,
        last_bot_draw_offer_deficit=round.last_bot_draw_offer_deficit,
    )


def player_offer_draw_to_bot(round: RoundState) -> RoundState:
    if round.game.winner is not None:
        return round

    if round.draw_offer_by == "black":
        return round

    if round.surrender_by is not None:
        return round

    round = clear_draw_message(round)

    if bot_should_give_up(round.game):
        return create_round_with_bot_surrender(round)

    if should_bot_accept_player_draw(round.game, round.difficulty):
        return RoundState(
            game=create_new_game(),
            difficulty=round.difficulty,
            player_score=round.player_score,
            computer_score=round.computer_score,
            draw_offer_by=None,
            draw_offer_message="Computer accepted the draw. New game started.",
            turn_number=0,
            bot_draw_offer_count=0,
            last_bot_draw_offer_turn=None,
            last_bot_draw_offer_deficit=None,
            surrender_by=None,
            surrender_message=None,
        )

    return RoundState(
        game=round.game,
        difficulty=round.difficulty,
        player_score=round.player_score,
        computer_score=round.computer_score,
        draw_offer_by=None,
        draw_offer_message="Computer declined the draw.",
        turn_number=round.turn_number,
        bot_draw_offer_count=round.bot_draw_offer_count,
        last_bot_draw_offer_turn=round.last_bot_draw_offer_turn,
        last_bot_draw_offer_deficit=round.last_bot_draw_offer_deficit,
        surrender_by=None,
        surrender_message=None,
    )