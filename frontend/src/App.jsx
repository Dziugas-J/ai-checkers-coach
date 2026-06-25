import { useEffect, useState } from "react";
import { CreateNewGame, GetLegalMoves, MakeMove } from "./Api";
import "./App.css";

function App() {
    const [game, set_game] = useState(null);
    const [loading, set_loading] = useState(false);
    const [selected_piece, set_selected_piece] = useState(null);
    const [possible_moves, set_possible_moves] = useState([]);

    async function NewGame() {
        set_loading(true);
        set_selected_piece(null);
        set_possible_moves([]);

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

            if (possible_move.is_capture) {
                square_class += " capture-move";
            }
        }

        return square_class;
    }

    function ClearSelection() {
        set_selected_piece(null);
        set_possible_moves([]);
    }

    async function SelectPiece(row, col) {
        const moves = await GetLegalMoves(game, row, col);

        if (moves.length === 0) {
            ClearSelection();
            return;
        }

        set_selected_piece({ row, col });
        set_possible_moves(moves);
    }

    async function ApplyMove(target_row, target_col) {
        const move = GetPossibleMove(target_row, target_col);

        if (!game || !selected_piece || !move) {
            return;
        }

        const updated_game = await MakeMove(
            game,
            selected_piece.row,
            selected_piece.col,
            target_row,
            target_col
        );

        set_game(updated_game);

        if (updated_game.must_continue_capture && updated_game.forced_piece) {
            set_selected_piece({
                row: updated_game.forced_piece.row,
                col: updated_game.forced_piece.col,
            });

            const next_moves = await GetLegalMoves(
                updated_game,
                updated_game.forced_piece.row,
                updated_game.forced_piece.col
            );

            set_possible_moves(next_moves);
            return;
        }

        ClearSelection();
    }

    async function HandleSquareClick(row, col) {
        if (!game) {
            return;
        }

        if (IsPossibleMove(row, col)) {
            await ApplyMove(row, col);
            return;
        }

        const piece = game.board[row][col];

        if (piece === "empty") {
            ClearSelection();
            return;
        }

        if (IsSelected(row, col)) {
            ClearSelection();
            return;
        }

        await SelectPiece(row, col);
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
                <div className="board">
                    {game.board.map((row, row_index) =>
                        row.map((piece, col_index) => {
                            const possible_move = GetPossibleMove(row_index, col_index);
                            const square_class = GetSquareClassName(
                                row_index,
                                col_index,
                                possible_move
                            );

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