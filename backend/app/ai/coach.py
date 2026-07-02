import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from app.ai.coach_prep import (
    board_has_king,
    get_legal_moves_text,
    get_position_text,
    legal_moves_include_promotion,
)
from app.game_logic.board import BOARD_SIZE
from app.game_logic.models import GameState, HintResponse


load_dotenv("../.env")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def square_to_position(square: str) -> tuple[int, int]:
    file_name = square[0].upper()
    rank = int(square[1:])

    col = ord(file_name) - ord("A")
    row = BOARD_SIZE - rank

    return row, col


def get_move_prefix(move_text: str) -> str:
    parts = move_text.split()

    if len(parts) < 3:
        return move_text

    return f"{parts[0]} -> {parts[2]}"


def get_hint_response_without_move(hint: str) -> HintResponse:
    return HintResponse(
        hint=hint,
        start_row=None,
        start_col=None,
        target_row=None,
        target_col=None,
    )


def get_hint_response_from_move(move_text: str, reason: str) -> HintResponse:
    move_prefix = get_move_prefix(move_text)
    parts = move_prefix.split()

    if len(parts) < 3:
        return get_hint_response_without_move(reason)

    start_square = parts[0]
    target_square = parts[2]

    start_row, start_col = square_to_position(start_square)
    target_row, target_col = square_to_position(target_square)

    return HintResponse(
        hint=reason,
        start_row=start_row,
        start_col=start_col,
        target_row=target_row,
        target_col=target_col,
    )


def find_matching_legal_move(selected_move: str, legal_moves: list[str]) -> str | None:
    if selected_move in legal_moves:
        return selected_move

    selected_prefix = get_move_prefix(selected_move)

    for legal_move in legal_moves:
        legal_prefix = get_move_prefix(legal_move)

        if legal_prefix == selected_prefix:
            return legal_move

    return None


def get_ai_hint(game: GameState) -> HintResponse:
    legal_moves = get_legal_moves_text(game)

    if len(legal_moves) == 0:
        return get_hint_response_without_move("No legal moves are available.")

    legal_moves_text = "\n".join(
        f"{index + 1}. {move}"
        for index, move in enumerate(legal_moves[:12])
    )

    king_can_be_discussed = (
        board_has_king(game)
        or legal_moves_include_promotion(legal_moves)
    )

    king_rule = ""

    if not king_can_be_discussed:
        king_rule = "- There are no kings and no promotion moves. Do not use the word king."

    prompt = f"""
    You are a checkers coach.

    White is the player.
    Black is the computer.
    Current player: {game.current_player}

    Board coordinates use A1 at White's bottom-left.

    {get_position_text(game)}

    Legal moves:
    {legal_moves_text}

    Rules:
    - Keep in mind its Lithuanian/Russian checkers ruling.
    - Choose only one move from the legal moves list.
    - The move must exactly match one move from the legal moves list.
    - Prefer moves marked as safe.
    - Avoid moves marked as warning or danger unless every listed move is risky.
    - Avoid moves that allow black to make a capture sequence.
    - Do not invent piece positions.
    - Do not invent captures.
    - Do not invent promotions.
    - Only mention kings if a king is listed on the board or the chosen move promotes to king.
    - Only say "captures" if the chosen legal move text contains "captures on", "black can capture", or "capture sequence".
    - Do not say a king reaches the back rank as a benefit.
    - The reason should explain why the move is useful.
    - The reason must not include the move notation.
    - Keep the reason under 18 words.
    {king_rule}

    Return only valid JSON in this format:
    {{
        "move": "exact move copied from the legal moves list",
        "reason": "short reason without move notation"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=120,
                temperature=0.1,
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0,
                ),
            ),
        )

    except Exception:
        return get_hint_response_without_move(
            "AI coach is unavailable right now. Try again later."
        )

    try:
        if response.text is None:
            raise ValueError("Empty Gemini response")

        data = json.loads(response.text)

        selected_move = data["move"].strip()
        reason = data["reason"].strip()

        if reason == "":
            raise ValueError("Empty hint reason")

    except Exception:
        return get_hint_response_without_move(
            "AI coach is unavailable right now. Try again later."
        )

    matching_legal_move = find_matching_legal_move(
        selected_move,
        legal_moves,
    )

    if matching_legal_move is None:
        return get_hint_response_without_move(
            "AI coach is unavailable right now. Try again later."
        )

    return get_hint_response_from_move(
        matching_legal_move,
        reason,
    )