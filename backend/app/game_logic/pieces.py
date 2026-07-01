from app.game_logic.models import Piece, Player


def get_piece_owner(piece: Piece) -> Player | None:
    if piece == "white" or piece == "white_king":
        return "white"
    elif piece == "black" or piece == "black_king":
        return "black"
    else:
        return None

def get_opponent_player(piece: Piece) -> Player | None:
    player = get_piece_owner(piece)

    if player == "white":
        return "black"
    elif player == "black":
        return "white"
    else:
        return None

def get_next_player(player: Player) -> Player:
    if player == "white":
        return "black"
    else:
        return "white"

def is_piece_king(piece: Piece) -> bool:
    return piece == "white_king" or piece == "black_king"

def promote_piece(piece: Piece, row: int) -> Piece:
    if piece == "white" and row == 0:
        return "white_king"
    elif piece == "black" and row == 7:
        return "black_king"
    else:
        return piece

def get_diagonal_directions() -> list[tuple[int, int]]:
    return [(-1, -1), (-1, 1), (1, -1), (1, 1)]

def get_legal_move_directions(piece: Piece) -> list[tuple[int, int]]:
    if is_piece_king(piece):
        return get_diagonal_directions()
    if piece == "white":
        return [(-1, -1), (-1, 1)]
    elif piece == "black":
        return [(1, -1),(1, 1),]
    else:
        return []