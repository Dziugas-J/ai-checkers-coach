import useControllers from "./useControllers";
import {
    capitalizeDifficulty,
    countPieces,
    getMoveForSquare,
    getSquareClassName,
    isSquareSelected,
} from "./helpers";
import "./styles/base.css";
import "./styles/board.css";
import "./styles/ui.css";

function App() {
    const {
        game,
        selectedPiece,
        possibleMoves,
        botDifficulty,
        hint,
        hintMove,
        hintLoading,
        difficultyDropdownOpen,
        playerScore,
        computerScore,
        hintMoveVisible,
        startNewGame,
        handleSquareClick,
        getHint,
        toggleDifficultyDropdown,
        selectDifficulty,
        drawOfferBy,
        drawOfferMessage,
        acceptDraw,
        declineDraw,
        offerDraw,
        surrenderBy,
        surrenderMessage,
    } = useControllers();

    function isHintStart(row, col) {
        if (hintMove === null) {
            return false;
        }

        return hintMove.startRow === row && hintMove.startCol === col;
    }

    function renderSurrenderPanel() {
        if (!surrenderMessage) {
            return null;
        }

        return (
            <div className="surrender-panel">
                <p>{surrenderMessage}</p>
                <span>New game starts in 3 seconds...</span>
            </div>
        );
    }

    function isHintTarget(row, col) {
        if (hintMove === null || !hintMoveVisible) {
            return false;
        }

        return hintMove.targetRow === row && hintMove.targetCol === col;
    }

    function isHintPath(row, col) {
        if (hintMove === null || game === null || !hintMoveVisible) {
            return false;
        }

        if (game.board[row][col] !== "empty") {
            return false;
        }

        const rowDistance = hintMove.targetRow - hintMove.startRow;
        const colDistance = hintMove.targetCol - hintMove.startCol;

        if (Math.abs(rowDistance) !== Math.abs(colDistance)) {
            return false;
        }

        const rowStep = rowDistance > 0 ? 1 : -1;
        const colStep = colDistance > 0 ? 1 : -1;

        let currentRow = hintMove.startRow + rowStep;
        let currentCol = hintMove.startCol + colStep;

        while (
            currentRow !== hintMove.targetRow &&
            currentCol !== hintMove.targetCol
        ) {
            if (currentRow === row && currentCol === col) {
                return true;
            }

            currentRow += rowStep;
            currentCol += colStep;
        }

        return false;
    }

    function renderPiece(piece, row, col) {
        if (piece === "empty") {
            return null;
        }

        let pieceClass = `piece ${piece}`;

        if (isSquareSelected(selectedPiece, row, col)) {
            pieceClass += " selected";
        }

        if (isHintStart(row, col)) {
            pieceClass += " hint-piece";
        }

        return (
            <div className={pieceClass}></div>
        );
    }

    function renderDrawPanel() {
        if (!drawOfferMessage) {
            return null;
        }

        if (drawOfferBy === "black") {
            return (
                <div className="draw-panel">
                    <p>{drawOfferMessage}</p>

                    <div className="draw-actions">
                        <button onClick={acceptDraw}>
                            Accept draw
                        </button>

                        <button onClick={declineDraw}>
                            Keep playing
                        </button>
                    </div>
                </div>
            );
        }

        return (
            <div className="draw-panel">
                <p>{drawOfferMessage}</p>
            </div>
        );
    }

    function renderGame() {
        if (!game) {
            return null;
        }

        return (
            <div className="game-content">
                <div className="game-screen">
                    <div className="board-area">
                        <section className="top-game-bar">
                            <div className="turn-pill">
                                Player <strong>{playerScore}</strong> :{" "}
                                <strong>{computerScore}</strong> Computer
                            </div>

                            <div className="piece-count">
                                <strong>{countPieces(game, "white")}</strong> white ·{" "}
                                <strong>{countPieces(game, "black")}</strong> black
                            </div>

                            <div className="custom-difficulty">
                                <button
                                    className="difficulty-select"
                                    onClick={toggleDifficultyDropdown}
                                >
                                    <span>
                                        {botDifficulty === null
                                            ? "Medium"
                                            : capitalizeDifficulty(botDifficulty)}
                                    </span>
                                </button>

                                {difficultyDropdownOpen && (
                                    <div className="difficulty-options">
                                        <button
                                            className={`difficulty-option ${botDifficulty === "easy" ? "active" : ""}`}
                                            onClick={() => selectDifficulty("easy")}
                                        >
                                            Easy
                                        </button>

                                        <button
                                            className={`difficulty-option ${botDifficulty === "medium" ? "active" : ""}`}
                                            onClick={() => selectDifficulty("medium")}
                                        >
                                            Medium
                                        </button>

                                        <button
                                            className={`difficulty-option ${botDifficulty === "hard" ? "active" : ""}`}
                                            onClick={() => selectDifficulty("hard")}
                                        >
                                            Hard
                                        </button>
                                    </div>
                                )}
                            </div>
                        </section>

                        <section className="board-section">
                            <div className="board">
                                {game.board.map((row, rowIndex) =>
                                    row.map((piece, colIndex) => {
                                        const possibleMove = getMoveForSquare(
                                            possibleMoves,
                                            rowIndex,
                                            colIndex
                                        );

                                        let squareClass = getSquareClassName(
                                            rowIndex,
                                            colIndex,
                                            possibleMove
                                        );

                                        if (isHintPath(rowIndex, colIndex)) {
                                            squareClass += " hint-path";
                                        }

                                        if (isHintTarget(rowIndex, colIndex)) {
                                            squareClass += " hint-target";
                                        }

                                        return (
                                            <div
                                                key={`${rowIndex}-${colIndex}`}
                                                className={squareClass}
                                                onClick={() =>
                                                    handleSquareClick(rowIndex, colIndex)
                                                }
                                            >
                                                {renderPiece(piece, rowIndex, colIndex)}
                                            </div>
                                        );
                                    })
                                )}
                            </div>

                            <p className="move-label">
                                {game.current_player === "white"
                                    ? "Your move (White)"
                                    : "Computer's move (Black)"}
                            </p>

                            {renderDrawPanel()}
                            {renderSurrenderPanel()}

                            <div className="game-buttons">
                                <button
                                    className="main-action-button"
                                    onClick={() => startNewGame(botDifficulty || "easy")}
                                >
                                    New game
                                </button>

                                <button
                                    className="secondary-action-button"
                                    onClick={offerDraw}
                                    disabled={
                                        drawOfferBy !== null ||
                                        surrenderBy !== null ||
                                        game.current_player !== "white"
                                    }
                                >
                                    Offer draw
                                </button>

                                <button
                                    className="secondary-action-button"
                                    onClick={getHint}
                                    disabled={
                                        hintLoading ||
                                        drawOfferBy !== null ||
                                        surrenderBy !== null
                                    }
                                >
                                    {hintLoading ? "..." : "Hint"}
                                </button>
                            </div>
                        </section>
                    </div>

                    <section className="coach-panel">
                        <div className="coach-header">
                            <h2>Checkers coach</h2>
                            <span>Hints for the current board</span>
                        </div>

                        {hint && (
                            <div className="hint-box">
                                <p>{hint}</p>
                            </div>
                        )}
                    </section>
                </div>
            </div>
        );
    }

    return (
        <main className="app">
            <h1>AI Checkers Coach</h1>

            {renderGame()}
        </main>
    );
}

export default App;