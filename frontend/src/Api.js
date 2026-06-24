const API_URL = "http://127.0.0.1:8000";

export async function CreateNewGame() {
    const response = await fetch(`${API_URL}/game/new`, {
        method: "POST",
    });

    const data = await response.json();
    return data;
}