const API_URL = "http://127.0.0.1:8000";

export async function CreateNewGame() {
    const response = await fetch(`${API_URL}/game/new`, {
        method: "POST",
    });

    const data = await response.json();
    return data;
}

export async function MakeMove(game, start_row, start_col, target_row, target_col) {
    const response = await fetch(`${API_URL}/game/move`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            game: game,
            start_row: start_row,
            start_col: start_col,
            target_row: target_row,
            target_col: target_col,
        }),
    });

    const data = await response.json();
    return data;
}

export async function GetLegalMoves(game, row, col) {
    const response = await fetch(`${API_URL}/game/legal-moves`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            game: game,
            row: row,
            col: col,
        }),
    });

    const data = await response.json();
    return data;
}