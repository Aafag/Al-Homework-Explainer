const API_BASE = "http://localhost:5000/api";

document.getElementById("askBtn").addEventListener("click", askQuestion);

// Ask question
async function askQuestion() {
    const question = document.getElementById("questionInput").value.trim();
    const resultDiv = document.getElementById("result");

    if (!question) {
        resultDiv.classList.remove("hidden");
        resultDiv.innerHTML = "⚠️ Please enter a question.";
        return;
    }

    resultDiv.classList.remove("hidden");
    resultDiv.innerHTML = "⏳ Generating explanation...";

    try {
        const response = await fetch(`${API_BASE}/questions`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Something went wrong");
        }

        resultDiv.innerHTML = `
            <h3>📖 Explanation</h3>
            <p>${data.explanation}</p>
        `;

        document.getElementById("questionInput").value = "";
        loadHistory();

    } catch (error) {
        resultDiv.innerHTML = `❌ Error: ${error.message}`;
    }
}

// Load previous questions
async function loadHistory() {
    const historyDiv = document.getElementById("history");

    try {
        const response = await fetch(`${API_BASE}/questions`);
        const data = await response.json();

        historyDiv.innerHTML = "";

        data.forEach(item => {
            const div = document.createElement("div");
            div.className = "history-item";

            div.innerHTML = `
                <strong>Q:</strong> ${item.question}
                <strong>A:</strong> ${item.explanation}
                <small>🕒 ${new Date(item.created_at).toLocaleString()}</small>
            `;

            historyDiv.appendChild(div);
        });

    } catch (error) {
        historyDiv.innerHTML = "⚠️ Failed to load history.";
    }
}

// Load history on page load
window.onload = loadHistory;
