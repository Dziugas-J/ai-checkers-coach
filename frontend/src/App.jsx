import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
    const [game, setGame] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [selectedPiece, setSelectedPiece] = useState(null);
    const [possibleMoves, setPossibleMoves] = useState([]);

    async function newGame() {
        try {
            setLoading(true);
            setError("");
            setSelectedPiece(null);
            setPossibleMoves([]);

            const response = await fetch(`${API_URL}/game/new`, {
                method: "POST",
            });

            if (!response.ok) {
                throw new Error("Failed to create new game");
            }

            const data = await response.json();
            setGame(data);
        }
        catch (err) {
            setError(err.message);
        }
        finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        newGame();
    }, []);

    function isInsideBoard(row, col) {
        return row >= 0 && row < 8 && col >= 0 && col < 8;
    }

    function getPossibleMoves(board, row, col) {
        const piece = board[row][col];

        if (piece === "empty") {
            return [];
        }

        const direction = piece === "white" ? -1 : 1;

        const moveCandidates = [
            { row: row + direction, col: col - 1 },
            { row: row + direction, col: col + 1 },
        ];

        return moveCandidates.filter((move) => {
            if (!isInsideBoard(move.row, move.col)) {
                return false;
            }

            return board[move.row][move.col] === "empty";
        });
    }

    function isSelected(row, col) {
        return (
            selectedPiece !== null &&
            selectedPiece.row === row &&
            selectedPiece.col === col
        );
    }

    function isPossibleMove(row, col) {
        return possibleMoves.some(
            (move) => move.row === row && move.col === col
        );
    }

    function handleSquareClick(row, col) {
        if (!game) {
            return;
        }

        const piece = game.board[row][col];
        const humanPlayer = "white"

        if (piece === "empty" || piece !== humanPlayer) {
            setSelectedPiece(null);
            setPossibleMoves([]);
            return;
        }

        if (isSelected(row, col)) {
            setSelectedPiece(null);
            setPossibleMoves([]);
            return;
        }

        setSelectedPiece({ row, col });
        setPossibleMoves(getPossibleMoves(game.board, row, col));
    }

    function renderPiece(piece, row, col) {
        if (piece === "empty") {
            return null;
        }

        return (
            <div className={`piece ${piece} ${isSelected(row, col) ? "selected" : ""}`}></div>
        );
    }

    return (
        <main className="app">
            <h1>AI Checkers Coach</h1>

            <button onClick={newGame} disabled={loading}>
                {loading ? "Loading..." : "New Game"}
            </button>

            {error && <p className="error">{error}</p>}

            {game && (
                <section className="game-info">
                    <p>
                        <strong>Current player:</strong> {game.current_player}
                    </p>
                    <div className="board">
                        {game.board.map((row, rowIndex) =>
                            row.map((piece, colIndex) => {
                                const isDarkSquare = (rowIndex + colIndex) % 2 === 1;

                                return (
                                    <div
                                        key={`${rowIndex}-${colIndex}`}
                                        className={`square ${isDarkSquare ? "dark" : "light"} ${isPossibleMove(rowIndex, colIndex) ? "possible-move" : ""}`}
                                        onClick={() => handleSquareClick(rowIndex, colIndex)}
                                    >
                                        {renderPiece(piece, rowIndex, colIndex)}
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