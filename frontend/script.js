const form = document.getElementById("scoutForm");
const jdInput = document.getElementById("jd");
const topKInput = document.getElementById("topk");
const runButton = document.getElementById("runButton");
const sampleButton = document.getElementById("sampleButton");
const resultsDiv = document.getElementById("results");
const emptyState = document.getElementById("emptyState");
const downloadButton = document.getElementById("downloadButton");
const runState = document.getElementById("runState");
const toast = document.getElementById("toast");
const metricCandidates = document.getElementById("metricCandidates");
const metricHigh = document.getElementById("metricHigh");
const metricSession = document.getElementById("metricSession");
const steps = Array.from(document.querySelectorAll(".step"));

const sampleJD = `We are hiring a Data Scientist with experience in Python, SQL, machine learning, and LLM applications. The candidate should be comfortable building models, working with business teams, and explaining analytical insights clearly.`;

let progressTimer = null;
let activeStepIndex = 0;

function escapeHTML(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showToast(message) {
    toast.textContent = message;
    toast.classList.remove("hidden");
    window.setTimeout(() => toast.classList.add("hidden"), 3800);
}

function resetSteps() {
    steps.forEach((step) => {
        step.classList.remove("is-active", "is-done", "is-failed");
    });
    activeStepIndex = 0;
}

function startStepAnimation() {
    resetSteps();
    steps[0].classList.add("is-active");

    progressTimer = window.setInterval(() => {
        steps[activeStepIndex]?.classList.remove("is-active");
        steps[activeStepIndex]?.classList.add("is-done");
        activeStepIndex = Math.min(activeStepIndex + 1, steps.length - 1);
        steps[activeStepIndex]?.classList.add("is-active");
    }, 1300);
}

function stopStepAnimation() {
    if (progressTimer) {
        window.clearInterval(progressTimer);
        progressTimer = null;
    }
}

function applyNodeStatus(nodeStatus = {}) {
    stopStepAnimation();

    steps.forEach((step) => {
        const status = nodeStatus[step.dataset.step];
        step.classList.remove("is-active", "is-done", "is-failed");

        if (status === "ok" || status === "skipped") {
            step.classList.add("is-done");
        } else if (status === "failed") {
            step.classList.add("is-failed");
        }
    });
}

function setBusy(isBusy) {
    runButton.disabled = isBusy;
    runButton.querySelector("span:last-child").textContent = isBusy ? "Scouting..." : "Run Scout";
    runState.textContent = isBusy ? "Running" : "Idle";
}

function configureDownload(sessionId) {
    if (!sessionId) {
        downloadButton.href = "#";
        downloadButton.classList.add("is-disabled");
        downloadButton.setAttribute("aria-disabled", "true");
        return;
    }

    downloadButton.href = `/export/${encodeURIComponent(sessionId)}`;
    downloadButton.classList.remove("is-disabled");
    downloadButton.setAttribute("aria-disabled", "false");
}

function updateMetrics(data) {
    const candidates = data.final_output || [];
    const highPriority = candidates.filter((candidate) => candidate.status === "High Priority").length;

    metricCandidates.textContent = candidates.length;
    metricHigh.textContent = highPriority;
    metricSession.textContent = data.session_id ? data.session_id.slice(0, 8) : "Ready";
}

function statusClass(status) {
    if (status === "High Priority") return "high";
    if (status === "Consider") return "consider";
    return "low";
}

function renderResults(candidates = []) {
    resultsDiv.innerHTML = "";
    emptyState.classList.toggle("hidden", candidates.length > 0);

    candidates.forEach((candidate) => {
        const className = statusClass(candidate.status);
        const score = Number(candidate.final_score || 0);
        const card = document.createElement("article");
        card.className = `candidate-card ${className}`;
        card.style.setProperty("--score", Math.max(0, Math.min(100, score)));

        card.innerHTML = `
            <div class="card-top">
                <div>
                    <h3>${escapeHTML(candidate.candidate_name)}</h3>
                    <span class="badge">${escapeHTML(candidate.status)}</span>
                </div>
                <div class="score-ring" aria-label="Final score ${escapeHTML(score)}">
                    <strong>${escapeHTML(score)}</strong>
                </div>
            </div>
            <div class="score-row">
                <div class="score-pill">
                    <span>Match</span>
                    <strong>${escapeHTML(candidate.match_score)}</strong>
                </div>
                <div class="score-pill">
                    <span>Interest</span>
                    <strong>${escapeHTML(candidate.interest_score)}</strong>
                </div>
            </div>
            <p class="card-text"><strong>Insight:</strong> ${escapeHTML(candidate.explanation)}</p>
            <p class="card-text"><strong>Summary:</strong> ${escapeHTML(candidate.conversation_summary)}</p>
        `;

        resultsDiv.appendChild(card);
    });
}

async function runAgent(event) {
    event.preventDefault();

    const jdText = jdInput.value.trim();
    const topK = Number.parseInt(topKInput.value, 10);

    if (!jdText) {
        showToast("Paste a job description first.");
        jdInput.focus();
        return;
    }

    setBusy(true);
    configureDownload(null);
    resultsDiv.innerHTML = "";
    emptyState.classList.remove("hidden");
    metricCandidates.textContent = "0";
    metricHigh.textContent = "0";
    metricSession.textContent = "Running";
    startStepAnimation();

    try {
        const response = await fetch("/scout", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                jd_text: jdText,
                top_k: Number.isFinite(topK) ? topK : 5
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail?.message || data.detail?.error || "Scout request failed.");
        }

        applyNodeStatus(data.node_status);
        updateMetrics(data);
        configureDownload(data.session_id);
        renderResults(data.final_output || []);

        if (data.error) {
            showToast(`Run completed with a warning: ${data.error}`);
        } else {
            runState.textContent = "Complete";
        }
    } catch (error) {
        stopStepAnimation();
        steps[activeStepIndex]?.classList.add("is-failed");
        runState.textContent = "Error";
        showToast(error.message || "Error connecting to API.");
    } finally {
        setBusy(false);
    }
}

form.addEventListener("submit", runAgent);

sampleButton.addEventListener("click", () => {
    jdInput.value = sampleJD;
    jdInput.focus();
});
