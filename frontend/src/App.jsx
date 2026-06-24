import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
    const [game, set_game] = useState(null);
    const [loading, set_loading] = useState(false);
    const [error, set_error] = useState("");
    const [selected_piece, set_selected_piece] = useState(null);
    const [possible_moves, set_possible_moves] = useState([]);
    const [must_continue_capture, set_must_continue_capture] = useState(false);

    async function NewGame() {
        try {
            set_loading(true);
            set_error("");
            set_selected_piece(null);
            set_possible_moves([]);
            set_must_continue_capture(false);

            const response = await fetch(`${API_URL}/game/new`, {
                method: "POST",
            });

            if (!response.ok) {
                throw new Error("Failed to create new game");
            }

            const data = await response.json();
            set_game(data);
        }
        catch (err) {
            set_error(err.message);
        }
        finally {
            set_loading(false);
        }
    }

    useEffect(() => {
        NewGame();
    }, []);

    function IsInsideBoard(row, col) {
        return row >= 0 && row < 8 && col >= 0 && col < 8;
    }

    function GetOpponent(piece) {
        if (piece === "white") {
            return "black";
        }

        if (piece === "black") {
            return "white";
        }

        return null;
    }

    function GetNextPlayer(player) {
        return player === "white" ? "black" : "white";
    }

    function GetPossibleMoves(board, row, col) {
        const piece = board[row][col];

        if (piece === "empty") {
            return [];
        }

        const opponent = GetOpponent(piece);
        const direction = piece === "white" ? -1 : 1;

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

        const capture_directions = [
            { row_direction: -1, col_direction: -1 },
            { row_direction: -1, col_direction: 1 },
            { row_direction: 1, col_direction: -1 },
            { row_direction: 1, col_direction: 1 },
        ];

        for (const capture_direction of capture_directions) {
            const middle_row = row + capture_direction.row_direction;
            const middle_col = col + capture_direction.col_direction;
            const target_row = row + capture_direction.row_direction * 2;
            const target_col = col + capture_direction.col_direction * 2;

            if (!IsInsideBoard(target_row, target_col)) {
                continue;
            }

            const middle_piece = board[middle_row][middle_col];
            const destination_piece = board[target_row][target_col];

            if (middle_piece === opponent && destination_piece === "empty") {
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

    function GetCaptureMoves(board, row, col) {
        return GetPossibleMoves(board, row, col).filter((move) => move.is_capture);
    }

    function PlayerHasCapture(board, player) {
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                if (board[row][col] !== player) {
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

    function IsSelected(row, col) {
        return (
            selected_piece !== null &&
            selected_piece.row === row &&
            selected_piece.col === col
        );
    }

    function GetPossibleMove(row, col) {
        return possible_moves.find(
            (move) => move.row === row && move.col === col
        );
    }

    function IsPossibleMove(row, col) {
        return GetPossibleMove(row, col) !== undefined;
    }

    function ApplyMove(target_row, target_col) {
        const move = GetPossibleMove(target_row, target_col);

        if (!game || !selected_piece || !move) {
            return;
        }

        const new_board = game.board.map((row) => [...row]);

        const selected_row = selected_piece.row;
        const selected_col = selected_piece.col;
        const moving_piece = new_board[selected_row][selected_col];

        new_board[selected_row][selected_col] = "empty";
        new_board[target_row][target_col] = moving_piece;

        if (move.is_capture && move.captured_piece) {
            new_board[move.captured_piece.row][move.captured_piece.col] = "empty";
        }

        if (move.is_capture) {
            const next_capture_moves = GetCaptureMoves(new_board, target_row, target_col);

            if (next_capture_moves.length > 0) {
                set_game({
                    ...game,
                    board: new_board,
                    current_player: game.current_player,
                    message: "Piece captured. Continue capture.",
                });

                set_selected_piece({
                    row: target_row,
                    col: target_col,
                });

                set_possible_moves(next_capture_moves);
                set_must_continue_capture(true);
                return;
            }
        }

        set_game({
            ...game,
            board: new_board,
            current_player: GetNextPlayer(game.current_player),
            message: move.is_capture ? "Piece captured" : "Piece moved",
        });

        set_selected_piece(null);
        set_possible_moves([]);
        set_must_continue_capture(false);
    }

    function HandleSquareClick(row, col) {
        if (!game) {
            return;
        }

        if (IsPossibleMove(row, col)) {
            ApplyMove(row, col);
            return;
        }

        if (must_continue_capture) {
            return;
        }

        const piece = game.board[row][col];

        if (piece === "empty") {
            set_selected_piece(null);
            set_possible_moves([]);
            return;
        }

        if (piece !== game.current_player) {
            set_selected_piece(null);
            set_possible_moves([]);
            return;
        }

        if (IsSelected(row, col)) {
            set_selected_piece(null);
            set_possible_moves([]);
            return;
        }

        const selected_piece_moves = GetPossibleMoves(game.board, row, col);
        const selected_piece_captures = selected_piece_moves.filter((move) => move.is_capture);
        const current_player_has_capture = PlayerHasCapture(game.board, game.current_player);

        if (current_player_has_capture && selected_piece_captures.length === 0) {
            set_selected_piece(null);
            set_possible_moves([]);

            set_game({
                ...game,
                message: "Capture is mandatory.",
            });

            return;
        }

        set_selected_piece({ row, col });
        set_possible_moves(selected_piece_moves);
    }

    function RenderPiece(piece, row, col) {
        if (piece === "empty") {
            return null;
        }

        return (
            <div className={`piece ${piece} ${IsSelected(row, col) ? "selected" : ""}`}></div>
        );
    }

    return (
        <main className="app">
            <h1>AI Checkers Coach</h1>

            <button onClick={NewGame} disabled={loading}>
                {loading ? "Loading..." : "New Game"}
            </button>

            {error && <p className="error">{error}</p>}

            {game && (
                <section className="game-info">
                    <p>
                        <strong>Current player:</strong> {game.current_player}
                    </p>

                    <p>
                        <strong>Message:</strong> {game.message}
                    </p>

                    <div className="board">
                        {game.board.map((row, row_index) =>
                            row.map((piece, col_index) => {
                                const is_dark_square = (row_index + col_index) % 2 === 1;
                                const possible_move = GetPossibleMove(row_index, col_index);

                                return (
                                    <div
                                        key={`${row_index}-${col_index}`}
                                        className={`square ${is_dark_square ? "dark" : "light"} ${
                                            possible_move ? "possible-move" : ""
                                        } ${possible_move?.is_capture ? "capture-move" : ""}`}
                                        onClick={() => HandleSquareClick(row_index, col_index)}
                                    >
                                        {RenderPiece(piece, row_index, col_index)}
                                    </div>
                                );
                            })
                        )}
                    </div>
                </section>
            )}
        </main>
    );
}

export default App;