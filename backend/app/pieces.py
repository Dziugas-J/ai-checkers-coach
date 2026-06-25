from app.models import Piece, Player


def GetPiecePlayer(piece: Piece) -> Player | None:
    if piece == "white" or piece == "white_king":
        return "white"
    elif piece == "black" or piece == "black_king":
        return "black"
    else:
        return None

def GetOpponent(piece: Piece) -> Player | None:
    player = GetPiecePlayer(piece)

    if player == "white":
        return "black"
    elif player == "black":
        return "white"
    else:
        return None

def GetNextPlayer(player: Player) -> Player:
    if player == "white":
        return "black"
    else:
        return "white"

def IsKing(piece: Piece) -> bool:
    return piece == "white_king" or piece == "black_king"

def PromotePieceIfNeeded(piece: Piece, row: int) -> Piece:
    if piece == "white" and row == 0:
        return "white_king"
    elif piece == "black" and row == 7:
        return "black_king"
    else:
        return piece

def GetCaptureDirections() -> list[tuple[int, int]]:
    return [(-1, -1), (-1, 1), (1, -1), (1, 1)]

def GetNormalMoveDirections(piece: Piece) -> list[tuple[int, int]]:
    if IsKing(piece):
        return GetCaptureDirections()
    if piece == "white":
        return [(-1, -1), (-1, 1)]
    elif piece == "black":
        return [(1, -1),(1, 1),]
    else:
        return []