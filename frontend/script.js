const API_BASE = "/api";

document.getElementById("askBtn").addEventListener("click", askQuestion);

marked.setOptions({
    breaks: true,
    gfm: true
});

function escapeHtml(text) {
    return text
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function renderMarkdown(markdown) {
    const rawHtml = marked.parse(markdown || "");
    return DOMPurify.sanitize(rawHtml);
}

function renderMath(container) {
    if (typeof renderMathInElement !== "function") {
        return;
    }

    renderMathInElement(container, {
        delimiters: [
            { left: "$$", right: "$$", display: true },
            { left: "$", right: "$", display: false }
        ],
        throwOnError: false
    });
}

function buildAnswerCard(title, content) {
    return `
        <h3>${title}</h3>
        <div class="answer-content">${renderMarkdown(content)}</div>
    `;
}

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

        resultDiv.innerHTML = buildAnswerCard("📖 Explanation", data.explanation);
        renderMath(resultDiv);

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
                <strong>Q:</strong>
                <p class="question-text">${escapeHtml(item.question)}</p>
                <strong>A:</strong>
                <div class="answer-content">${renderMarkdown(item.explanation)}</div>
                <small>🕒 ${new Date(item.created_at).toLocaleString()}</small>
            `;

            renderMath(div);

            historyDiv.appendChild(div);
        });

    } catch (error) {
        historyDiv.innerHTML = "⚠️ Failed to load history.";
    }
}


// Load history on page load
window.onload = loadHistory;
