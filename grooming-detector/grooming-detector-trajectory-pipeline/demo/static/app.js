const messagesEl = document.getElementById("messages");
const form = document.getElementById("form");
const input = document.getElementById("input");
const authorEl = document.getElementById("author");
const resetBtn = document.getElementById("reset");
const riskEl = document.getElementById("risk");
const lstmEl = document.getElementById("lstm");
const lstmThresholdEl = document.getElementById("lstm-threshold");
const weightedEl = document.getElementById("weighted");
const flagEl = document.getElementById("flag");
const featuresBody = document.querySelector("#features tbody");
const bannerEl = document.getElementById("flag-banner");
const bannerTextEl = document.getElementById("flag-banner-text");
const inspectingEl = document.getElementById("inspecting");

let convId = null;
const turns = []; // history: each entry is the full API response for that turn
let selectedTurn = null; // which turn is currently displayed in the right panel

async function ensureConversation() {
  if (convId) return convId;
  const res = await fetch("/api/new", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
  const data = await res.json();
  convId = data.conv_id;
  return convId;
}

function renderFeatures(features) {
  featuresBody.innerHTML = "";
  for (const [name, value] of Object.entries(features)) {
    const tr = document.createElement("tr");
    const td1 = document.createElement("td");
    td1.textContent = name;
    const td2 = document.createElement("td");
    td2.textContent = value.toFixed(3);
    tr.appendChild(td1);
    tr.appendChild(td2);
    featuresBody.appendChild(tr);
  }
}

function formatTimestamp(d) {
  const pad = (n) => String(n).padStart(2, "0");
  return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

function renderPanelForTurn(turnIdx) {
  if (turnIdx === null || turnIdx < 0 || turnIdx >= turns.length) return;
  const t = turns[turnIdx];
  const prev = turnIdx > 0 ? turns[turnIdx - 1] : null;
  const delta = prev !== null ? t.turn_score - prev.turn_score : null;

  riskEl.textContent = t.risk_score.toFixed(3);
  lstmEl.textContent =
    delta === null
      ? t.lstm_score.toFixed(3)
      : `${t.lstm_score.toFixed(3)} (delta ${delta >= 0 ? "+" : ""}${delta.toFixed(3)})`;
  lstmThresholdEl.textContent = t.lstm_threshold.toFixed(3);
  weightedEl.textContent = t.weighted_score.toFixed(3);
  lstmEl.classList.toggle("alarm", t.first_flagged_turn !== null);
  flagEl.textContent = t.first_flagged_turn === null ? "—" : `turn ${t.first_flagged_turn}`;
  flagEl.classList.toggle("alarm", t.first_flagged_turn !== null);
  renderFeatures(t.trajectory_features);

  inspectingEl.textContent = `Inspecting turn ${t.turn} · ${t.author}`;

  // highlight the selected message in the chat
  selectedTurn = turnIdx;
  document.querySelectorAll(".messages li").forEach((li) => {
    li.classList.toggle("selected", parseInt(li.dataset.turn, 10) === turnIdx);
  });
}

function appendMessage(data, timestamp) {
  const li = document.createElement("li");
  li.classList.add(data.author);
  li.dataset.turn = String(data.turn);
  if (data.first_flagged_turn !== null && data.turn === data.first_flagged_turn) {
    li.classList.add("flagged-turn");
  }

  const textSpan = document.createElement("div");
  textSpan.className = "text";
  textSpan.textContent = data.text;
  li.appendChild(textSpan);

  const meta = document.createElement("div");
  meta.className = "meta";
  const left = document.createElement("span");
  left.className = "meta-left";
  left.textContent = `${data.author} · turn ${data.turn} · ${timestamp}`;
  const right = document.createElement("span");
  right.className = "meta-right";
  right.innerHTML =
    `L1 <span class="num">${data.risk_score.toFixed(3)}</span> · ` +
    `LSTM <span class="num">${data.lstm_score.toFixed(3)}</span>`;
  meta.appendChild(left);
  meta.appendChild(right);
  li.appendChild(meta);

  li.addEventListener("click", () => {
    const idx = parseInt(li.dataset.turn, 10);
    renderPanelForTurn(idx);
  });

  messagesEl.appendChild(li);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function updateBanner(firstFlagged, lstmScore) {
  if (firstFlagged === null) {
    bannerEl.classList.remove("active");
    bannerTextEl.textContent = "";
    return;
  }
  bannerEl.classList.add("active");
  bannerTextEl.textContent =
    `Conversation flagged - LSTM first crossed its validation-selected threshold at turn ${firstFlagged}. ` +
    `Current LSTM score: ${lstmScore.toFixed(3)}.`;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  const author = authorEl.value;
  await ensureConversation();

  const res = await fetch("/api/message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conv_id: convId, text, author }),
  });
  if (!res.ok) return;
  const data = await res.json();

  turns.push(data);
  const ts = formatTimestamp(new Date());
  appendMessage(data, ts);
  updateBanner(data.first_flagged_turn, data.turn_score);
  // Auto-jump to the new turn unless the user is inspecting an older one;
  // a fresh send is usually what they want to see scored.
  renderPanelForTurn(turns.length - 1);
});

resetBtn.addEventListener("click", async () => {
  if (convId) {
    await fetch("/api/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conv_id: convId }),
    });
  }
  convId = null;
  turns.length = 0;
  selectedTurn = null;
  messagesEl.innerHTML = "";
  featuresBody.innerHTML = "";
  riskEl.textContent = "—";
  lstmEl.textContent = "-";
  lstmThresholdEl.textContent = "-";
  weightedEl.textContent = "—";
  flagEl.textContent = "—";
  lstmEl.classList.remove("alarm");
  flagEl.classList.remove("alarm");
  bannerEl.classList.remove("active");
  bannerTextEl.textContent = "";
  inspectingEl.textContent = "Click any message to inspect its turn";
});
