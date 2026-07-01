import { useEffect, useState } from "react";
import {
    fetchNewRound,
    fetchPlayerLegalMoves,
    sendPlayerMove,
    sendBotMove,
    fetchPlayerHint,
    sendAcceptBotDraw,
    sendDeclineBotDraw,
    sendPlayerDrawOffer,
    sendFinishBotSurrender,
} from "./Api";
import {
    getMoveForSquare,
    isPossibleMoveSquare,
    isSquareSelected,
    waitHalfSecond,
} from "./helpers";

function useControllers() {
    const [round, setRound] = useState(null);
    const [selectedPiece, setSelectedPiece] = useState(null);
    const [possibleMoves, setPossibleMoves] = useState([]);
    const [hint, setHint] = useState("");
    const [hintMove, setHintMove] = useState(null);
    const [hintLoading, setHintLoading] = useState(false);
    const [difficultyDropdownOpen, setDifficultyDropdownOpen] = useState(false);
    const [hintMoveVisible, setHintMoveVisible] = useState(false);

    const game = round ? round.game : null;
    const botDifficulty = round ? round.difficulty : "easy";
    const playerScore = round ? round.player_score : 0;
    const computerScore = round ? round.computer_score : 0;
    const drawOfferBy = round ? round.draw_offer_by : null;
    const drawOfferMessage = round ? round.draw_offer_message : null;
    const surrenderBy = round ? round.surrender_by : null;
    const surrenderMessage = round ? round.surrender_message : null;

    async function loadPreviewGame() {
        const data = await fetchNewRound("easy");
        setRound(data);
    }

    async function startNewGame(difficulty) {
        setSelectedPiece(null);
        setPossibleMoves([]);
        setHint("");
        setHintMove(null);
        setHintLoading(false);
        setHintMoveVisible(false);

        const data = await fetchNewRound(difficulty);
        setRound(data);
    }

    useEffect(() => {
        loadPreviewGame();
    }, []);

    async function getHint() {
        if (!round || hintLoading) {
            return;
        }

        if (drawOfferBy === "black") {
            return;
        }

        if (surrenderBy !== null) {
            return;
        }

        if (game && game.current_player !== "white") {
            return;
        }

        if (hint !== "") {
            return;
        }

        setHintLoading(true);
        setHintMoveVisible(false);

        try {
            const data = await fetchPlayerHint(round);
            setHint(data.hint);

            if (
                data.start_row !== null &&
                data.start_col !== null &&
                data.target_row !== null &&
                data.target_col !== null
            ) {
                setHintMove({
                    startRow: data.start_row,
                    startCol: data.start_col,
                    targetRow: data.target_row,
                    targetCol: data.target_col,
                });
            }
            else {
                setHintMove(null);
            }
        }
        catch {
            setHintMove(null);
        }

        setHintLoading(false);
    }

    function clearHint() {
        setHint("");
        setHintMove(null);
        setHintLoading(false);
        setHintMoveVisible(false);
    }

    function clearSelectedPiece() {
        setSelectedPiece(null);
        setPossibleMoves([]);
        setHintMoveVisible(false);
    }

    async function selectPieceAndLoadMoves(row, col) {
        if (!round) {
            return;
        }

        const moves = await fetchPlayerLegalMoves(round, row, col);

        if (moves.length === 0) {
            clearSelectedPiece();
            return;
        }

        setSelectedPiece({ row, col });
        setPossibleMoves(moves);
    }

    async function applySelectedMove(targetRow, targetCol) {
        const selectedMove = getMoveForSquare(
            possibleMoves,
            targetRow,
            targetCol
        );

        if (!round || !game || !selectedPiece || !selectedMove) {
            return;
        }

        const moveStartRow = selectedPiece.row;
        const moveStartCol = selectedPiece.col;

        clearSelectedPiece();
        clearHint();

        const updatedRound = await sendPlayerMove(
            round,
            moveStartRow,
            moveStartCol,
            targetRow,
            targetCol
        );

        setRound(updatedRound);

        if (
            updatedRound.game.must_continue_capture &&
            updatedRound.game.forced_piece
        ) {
            setSelectedPiece({
                row: updatedRound.game.forced_piece.row,
                col: updatedRound.game.forced_piece.col,
            });

            const nextMoves = await fetchPlayerLegalMoves(
                updatedRound,
                updatedRound.game.forced_piece.row,
                updatedRound.game.forced_piece.col
            );

            setPossibleMoves(nextMoves);
            return;
        }

        let currentRound = updatedRound;

        while (
            currentRound.game.current_player === "black" &&
            currentRound.game.winner === null &&
            currentRound.surrender_by === null
        ) {
            await waitHalfSecond();

            currentRound = await sendBotMove(currentRound);
            setRound(currentRound);

            if (currentRound.surrender_by !== null) {
                return;
            }
        }

        clearSelectedPiece();
    }

    async function handleSquareClick(row, col) {
        if (!round || !game) {
            return;
        }

        if (drawOfferBy === "black") {
            return;
        }

        if (surrenderBy !== null) {
            return;
        }

        if (game.current_player === "black") {
            return;
        }

        if (
            hintMove &&
            hintMove.startRow === row &&
            hintMove.startCol === col
        ) {
            setHintMoveVisible(true);
        }

        if (isPossibleMoveSquare(possibleMoves, row, col)) {
            await applySelectedMove(row, col);
            return;
        }

        const piece = game.board[row][col];

        if (piece === "empty") {
            clearSelectedPiece();
            return;
        }

        if (isSquareSelected(selectedPiece, row, col)) {
            clearSelectedPiece();
            return;
        }

        await selectPieceAndLoadMoves(row, col);
    }

    function toggleDifficultyDropdown() {
        setDifficultyDropdownOpen(!difficultyDropdownOpen);
    }

    async function selectDifficulty(newDifficulty) {
        setDifficultyDropdownOpen(false);

        if (newDifficulty === botDifficulty) {
            return;
        }

        await startNewGame(newDifficulty);
    }

    async function acceptDraw() {
        if (!round) {
            return;
        }

        clearSelectedPiece();
        clearHint();

        const updatedRound = await sendAcceptBotDraw(round);
        setRound(updatedRound);
    }

    async function declineDraw() {
        if (!round) {
            return;
        }

        clearSelectedPiece();

        const updatedRound = await sendDeclineBotDraw(round);
        setRound(updatedRound);
    }

    useEffect(() => {
        if (!round) {
            return;
        }

        if (surrenderBy !== "black") {
            return;
        }

        const surrenderedRound = round;

        const timeoutId = setTimeout(async () => {
            clearSelectedPiece();
            clearHint();

            const updatedRound = await sendFinishBotSurrender(surrenderedRound);
            setRound(updatedRound);
        }, 3000);

        return () => clearTimeout(timeoutId);
    }, [surrenderBy]);

    async function offerDraw() {
        if (!round) {
            return;
        }

        if (surrenderBy !== null) {
            return;
        }

        clearSelectedPiece();
        clearHint();

        const updatedRound = await sendPlayerDrawOffer(round);
        setRound(updatedRound);
    }

    return {
        game,
        selectedPiece,
        possibleMoves,
        botDifficulty,
        hint,
        hintMove,
        hintMoveVisible,
        hintLoading,
        difficultyDropdownOpen,
        playerScore,
        computerScore,
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
    };
}

export default useControllers;