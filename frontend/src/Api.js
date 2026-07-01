const API_URL = "http://127.0.0.1:8000";

export async function fetchNewRound(difficulty) {
    const response = await fetch(`${API_URL}/round/new`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            difficulty,
        }),
    });

    return await response.json();
}

export async function fetchRoundLegalMoves(round, row, col) {
    const response = await fetch(`${API_URL}/round/legal-moves`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            round,
            row,
            col,
        }),
    });

    return await response.json();
}

export async function sendRoundMove(
    round,
    startRow,
    startCol,
    targetRow,
    targetCol
) {
    const response = await fetch(`${API_URL}/round/move`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            round,
            start_row: startRow,
            start_col: startCol,
            target_row: targetRow,
            target_col: targetCol,
        }),
    });

    return await response.json();
}

export async function fetchRoundHint(round) {
    const response = await fetch(`${API_URL}/round/hint`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            round,
        }),
    });

    return await response.json();
}

export async function sendRoundBotMove(round) {
    const response = await fetch(`${API_URL}/round/bot-move`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            round,
        }),
    });

    return await response.json();
}

export async function sendDrawAccept(round) {
    const response = await fetch(`${API_URL}/round/draw/accept`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            round,
        }),
    });

    return await response.json();
}

export async function sendDrawDecline(round) {
    const response = await fetch(`${API_URL}/round/draw/decline`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            round,
        }),
    });

    return await response.json();
}

export async function sendDrawOffer(round) {
    const response = await fetch(`${API_URL}/round/draw/offer`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            round,
        }),
    });

    return await response.json();
}

export async function sendFinishBotSurrender(round) {
    const response = await fetch(`${API_URL}/round/surrender/finish`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            round,
        }),
    });

    return await response.json();
}