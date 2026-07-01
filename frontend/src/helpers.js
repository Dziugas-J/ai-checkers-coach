export function getMoveForSquare(possibleMoves, row, col) {
    return possibleMoves.find(
        (move) => move.row === row && move.col === col
    );
}

export function isPossibleMoveSquare(possibleMoves, row, col) {
    return getMoveForSquare(possibleMoves, row, col) !== undefined;
}

export function isSquareSelected(selectedPiece, row, col) {
    return (
        selectedPiece !== null &&
        selectedPiece.row === row &&
        selectedPiece.col === col
    );
}

export function getSquareClassName(row, col, possibleMove) {
    let squareClass = "square";

    const isDarkSquare = (row + col) % 2 === 1;

    if (isDarkSquare) {
        squareClass += " dark";
    }
    else {
        squareClass += " light";
    }

    if (possibleMove) {
        squareClass += " possible-move";

        if (possibleMove.is_capture) {
            squareClass += " capture-move";
        }
    }

    return squareClass;
}

export function countPieces(game, player) {
    if (!game) {
        return 0;
    }

    let count = 0;

    for (const row of game.board) {
        for (const piece of row) {
            if (player === "white") {
                if (piece === "white" || piece === "white_king") {
                    count += 1;
                }
            }

            if (player === "black") {
                if (piece === "black" || piece === "black_king") {
                    count += 1;
                }
            }
        }
    }

    return count;
}

export function capitalizeDifficulty(difficulty) {
    if (!difficulty) {
        return "Medium";
    }

    return difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
}

export function waitHalfSecond() {
    return new Promise((resolve) => {
        setTimeout(resolve, 500);
    });
}