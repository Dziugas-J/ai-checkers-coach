export function IsInsideBoard(row, col) {
    return row >= 0 && row < 8 && col >= 0 && col < 8;
}

export function GetPiecePlayer(piece) {
    if (piece === "white" || piece === "white_king") {
        return "white";
    }

    if (piece === "black" || piece === "black_king") {
        return "black";
    }

    return null;
}

export function GetOpponent(piece) {
    const player = GetPiecePlayer(piece);

    if (player === "white") {
        return "black";
    }

    if (player === "black") {
        return "white";
    }

    return null;
}

export function GetNextPlayer(player) {
    if (player === "white") {
        return "black";
    }
    return "white";
}

export function IsKing(piece) {
    return piece === "white_king" || piece === "black_king";
}

export function PromotePieceIfNeeded(piece, row) {
    if (piece === "white" && row === 0) {
        return "white_king";
    }

    if (piece === "black" && row === 7) {
        return "black_king";
    }

    return piece;
}

export function GetCaptureDirections() {
    return [
        { row_direction: -1, col_direction: -1 },
        { row_direction: -1, col_direction: 1 },
        { row_direction: 1, col_direction: -1 },
        { row_direction: 1, col_direction: 1 },
    ];
}

export function GetPossibleMoves(board, row, col) {
    const piece = board[row][col];

    if (piece === "empty") {
        return [];
    }

    if (IsKing(piece)) {
        return GetKingPossibleMoves(board, row, col);
    }

    return GetRegularPiecePossibleMoves(board, row, col);
}

export function GetRegularPiecePossibleMoves(board, row, col) {
    const piece = board[row][col];
    const opponent = GetOpponent(piece);
    let direction = 1;

    if (piece === "white") {
        direction = -1;
    }

    const normal_moves = [];
    const capture_moves = [];

    const move_candidates = [
        { row: row + direction, col: col - 1 },
        { row: row + direction, col: col + 1 },
    ];

    for (const move of move_candidates) {
        if (
            IsInsideBoard(move.row, move.col) &&
            board[move.row][move.col] === "empty"
        ) {
            normal_moves.push({
                row: move.row,
                col: move.col,
                is_capture: false,
                captured_piece: null,
            });
        }
    }

    const capture_directions = GetCaptureDirections();

    for (const direction of capture_directions) {
        const middle_row = row + direction.row_direction;
        const middle_col = col + direction.col_direction;
        const target_row = row + direction.row_direction * 2;
        const target_col = col + direction.col_direction * 2;

        if (!IsInsideBoard(target_row, target_col)) {
            continue;
        }

        const middle_piece = board[middle_row][middle_col];
        const destination_piece = board[target_row][target_col];

        if (
            GetPiecePlayer(middle_piece) === opponent &&
            destination_piece === "empty"
        ) {
            capture_moves.push({
                row: target_row,
                col: target_col,
                is_capture: true,
                captured_piece: {
                    row: middle_row,
                    col: middle_col,
                },
            });
        }
    }

    if (capture_moves.length > 0) {
        return capture_moves;
    }

    return normal_moves;
}

export function GetKingPossibleMoves(board, row, col) {
    const piece = board[row][col];
    const piece_player = GetPiecePlayer(piece);
    const opponent = GetOpponent(piece);

    const normal_moves = [];
    const capture_moves = [];

    const directions = GetCaptureDirections();

    for (const direction of directions) {
        let current_row = row + direction.row_direction;
        let current_col = col + direction.col_direction;

        let captured_piece = null;

        while (IsInsideBoard(current_row, current_col)) {
            const current_piece = board[current_row][current_col];
            const current_piece_player = GetPiecePlayer(current_piece);

            if (current_piece === "empty") {
                if (captured_piece === null) {
                    normal_moves.push({
                        row: current_row,
                        col: current_col,
                        is_capture: false,
                        captured_piece: null,
                    });
                } else {
                    capture_moves.push({
                        row: current_row,
                        col: current_col,
                        is_capture: true,
                        captured_piece: captured_piece,
                    });
                }

                current_row += direction.row_direction;
                current_col += direction.col_direction;
                continue;
            }

            if (current_piece_player === piece_player) {
                break;
            }

            if (current_piece_player === opponent) {
                if (captured_piece !== null) {
                    break;
                }

                captured_piece = {
                    row: current_row,
                    col: current_col,
                };

                current_row += direction.row_direction;
                current_col += direction.col_direction;
                continue;
            }

            break;
        }
    }

    if (capture_moves.length > 0) {
        return capture_moves;
    }

    return normal_moves;
}

export function GetCaptureMoves(board, row, col) {
    return GetPossibleMoves(board, row, col).filter((move) => move.is_capture);
}

export function PlayerHasCapture(board, player) {
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const piece = board[row][col];

            if (GetPiecePlayer(piece) !== player) {
                continue;
            }

            const captures = GetCaptureMoves(board, row, col);

            if (captures.length > 0) {
                return true;
            }
        }
    }

    return false;
}