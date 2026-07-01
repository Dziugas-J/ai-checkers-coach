const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function postJson(path, body) {
    const response = await fetch(`${API_URL}${path}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        throw new Error(await response.text());
    }

    return response.json();
}

export function fetchNewRound(difficulty) {
    return postJson("/round/new", { difficulty });
}

export function fetchPlayerLegalMoves(round, row, col) {
    return postJson("/round/legal-moves", { round, row, col });
}

export function sendPlayerMove(round, startRow, startCol, targetRow, targetCol) {
    return postJson("/round/move", {
        round,
        start_row: startRow,
        start_col: startCol,
        target_row: targetRow,
        target_col: targetCol,
    });
}

export function fetchPlayerHint(round) {
    return postJson("/round/hint", { round });
}

export function sendBotMove(round) {
    return postJson("/round/bot-move", { round });
}

export function sendAcceptBotDraw(round) {
    return postJson("/round/draw/accept", { round });
}

export function sendDeclineBotDraw(round) {
    return postJson("/round/draw/decline", { round });
}

export function sendPlayerDrawOffer(round) {
    return postJson("/round/draw/offer", { round });
}

export function sendFinishBotSurrender(round) {
    return postJson("/round/surrender/finish", { round });
}
