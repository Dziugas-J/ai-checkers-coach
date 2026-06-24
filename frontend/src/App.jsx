import "./App.css";
import { 
    useEffect, 
    useState } from "react";
import { 
    CreateNewGame } from "./Api";

import {
    GetCaptureMoves,
    GetNextPlayer,
    GetPiecePlayer,
    GetPossibleMoves,
    PlayerHasCapture,
    PromotePieceIfNeeded,
} from "./GameLogic";

function App() {
    const [game, set_game] = useState(null);
    const [loading, set_loading] = useState(false);
    const [selected_piece, set_selected_piece] = useState(null);
    const [possible_moves, set_possible_moves] = useState([]);
    const [must_continue_capture, set_must_continue_capture] = useState(false);

    async function NewGame() {
        set_loading(true);
        set_selected_piece(null);
        set_possible_moves([]);
        set_must_continue_capture(false);

        const data = await CreateNewGame();
        set_game(data);

        set_loading(false);
    }

    useEffect(() => {
        NewGame();
    }, []);

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

    function GetNewGameButtonText() {
        if (loading) {
            return "Loading...";
        }

        return "New Game";
    }

    function GetSquareClassName(row, col, possible_move) {
        let square_class = "square";

        const is_dark_square = (row + col) % 2 === 1;

        if (is_dark_square) {
            square_class += " dark";
        }
        else {
            square_class += " light";
        }

        if (possible_move) {
            square_class += " possible-move";
        }

        if (possible_move && possible_move.is_capture) {
            square_class += " capture-move";
        }

        return square_class;
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

        const promoted_piece = PromotePieceIfNeeded(moving_piece, target_row);
        const was_promoted = promoted_piece !== moving_piece;

        new_board[target_row][target_col] = promoted_piece;

        if (move.is_capture && move.captured_piece) {
            new_board[move.captured_piece.row][move.captured_piece.col] = "empty";
        }

        if (move.is_capture) {
            const next_capture_moves = GetCaptureMoves(new_board, target_row, target_col);

            if (next_capture_moves.length > 0) {
                let message = "Piece captured. Continue capture.";

                if (was_promoted) {
                    message = "Piece promoted to king. Continue capture.";
                }

                set_game({
                    ...game,
                    board: new_board,
                    current_player: game.current_player,
                    message: message,
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

        let message = "Piece moved";

        if (move.is_capture) {
            message = "Piece captured";
        }

        if (was_promoted) {
            message = "Piece promoted to king";
        }

        set_game({
            ...game,
            board: new_board,
            current_player: GetNextPlayer(game.current_player),
            message: message,
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

        if (GetPiecePlayer(piece) !== game.current_player) {
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

        let piece_class = `piece ${piece}`;

        if (IsSelected(row, col)) {
            piece_class += " selected";
        }

        return (
            <div className={piece_class}></div>
        );
    }

    function RenderGame() {
        if (!game) {
            return null;
        }

        return (
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
                            const possible_move = GetPossibleMove(row_index, col_index);
                            let square_class = GetSquareClassName(
                                row_index,
                                col_index,
                                possible_move
                            );

                            if (possible_move) {
                                if (possible_move.is_capture) {
                                    square_class += " capture-move";
                                }
                            }

                            return (
                                <div
                                    key={`${row_index}-${col_index}`}
                                    className={square_class}
                                    onClick={() => HandleSquareClick(row_index, col_index)}
                                >
                                    {RenderPiece(piece, row_index, col_index)}
                                </div>
                            );
                        })
                    )}
                </div>
            </section>
        );
    }

    return (
        <main className="app">
            <h1>AI Checkers Coach</h1>

            <button onClick={NewGame} disabled={loading}>
                {GetNewGameButtonText()}
            </button>

            {RenderGame()}
        </main>
    );
}

export default App;