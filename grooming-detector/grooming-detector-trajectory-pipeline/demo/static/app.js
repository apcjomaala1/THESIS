const messagesEl = document.getElementById("messages");
const emptyStateEl = document.getElementById("empty-state");
const form = document.getElementById("form");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const authorEl = document.getElementById("author");
const resetBtn = document.getElementById("reset");
const composerSpeakerEl = document.getElementById("composer-speaker");
const composerAuthorLabelEl = document.getElementById("composer-author-label");
const composerStatusEl = document.getElementById("composer-status");

const riskEl = document.getElementById("risk");
const lstmEl = document.getElementById("lstm");
const lstmThresholdEl = document.getElementById("lstm-threshold");
const thresholdDistanceEl = document.getElementById("threshold-distance");
const sequenceLengthEl = document.getElementById("sequence-length");
const weightedEl = document.getElementById("weighted");
const weightedThresholdEl = document.getElementById("weighted-threshold");
const flagEl = document.getElementById("flag");
const crossingNoteEl = document.getElementById("crossing-note");
const turnPillEl = document.getElementById("turn-pill");
const outputStateEl = document.getElementById("output-state");
const outputStateLabelEl = document.getElementById("output-state-label");
const scoreDeltaEl = document.getElementById("score-delta");
const scorePercentEl = document.getElementById("score-percent");
const scoreFillEl = document.getElementById("score-fill");
const thresholdMarkerEl = document.getElementById("threshold-marker");

const featuresEl = document.getElementById("features");
const chartEl = document.getElementById("trajectory-chart");
const trajectoryBarsEl = document.getElementById("trajectory-bars");
const timelineThresholdEl = document.getElementById("timeline-threshold");
const bannerEl = document.getElementById("flag-banner");
const bannerTextEl = document.getElementById("flag-banner-text");

let convId = null;
const turns = [];
let selectedTurn = null;

const featureLabels = {
  current_score: "Current Layer 1 proxy",
  peak_score: "Peak proxy score so far",
  rate_of_change: "Score rate of change",
  spike_count: "Proxy spike count",
  spike_then_drop: "Spike-then-drop signal",
  topic_drift: "Topic drift from centroid",
  turn_taking_imbalance: "Turn-taking imbalance",
  conversation_velocity: "Conversation velocity",
};

async function readJsonOrThrow(response) {
  let payload = {};
  try {
    payload = await response.json();
  } catch (error) {
    throw new Error("The local demo returned an unreadable response.");
  }
  if (!response.ok) {
    throw new Error(payload.error || "The local demo could not score that turn.");
  }
  return payload;
}

async function ensureConversation() {
  if (convId) return convId;
  const response = await fetch("/api/new", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: "{}",
  });
  const data = await readJsonOrThrow(response);
  convId = data.conv_id;
  return convId;
}

function friendlyFeatureName(name) {
  if (featureLabels[name]) return featureLabels[name];
  return name.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function renderFeatures(features) {
  featuresEl.innerHTML = "";
  for (const [name, value] of Object.entries(features)) {
    const row = document.createElement("div");
    row.className = "feature-row";

    const label = document.createElement("span");
    label.className = "feature-name";
    label.textContent = friendlyFeatureName(name);

    const number = document.createElement("strong");
    number.className = "feature-value";
    number.textContent = Number(value).toFixed(3);

    row.append(label, number);
    featuresEl.appendChild(row);
  }
}

function formatTimestamp(date) {
  const pad = (number) => String(number).padStart(2, "0");
  return `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function setOutputState(turn) {
  outputStateEl.classList.remove("state-idle", "state-below", "state-above");
  if (turn.flagged_now) {
    outputStateEl.classList.add("state-above");
    outputStateLabelEl.textContent = "Development threshold crossed";
  } else if (turn.first_flagged_turn !== null) {
    outputStateEl.classList.add("state-above");
    outputStateLabelEl.textContent = "Previously crossed threshold";
  } else {
    outputStateEl.classList.add("state-below");
    outputStateLabelEl.textContent = "Below development threshold";
  }
}

function renderTimeline() {
  trajectoryBarsEl.innerHTML = "";
  if (turns.length === 0) {
    chartEl.classList.add("empty-chart");
    const empty = document.createElement("p");
    empty.id = "timeline-empty";
    empty.textContent = "Scores will build here turn by turn.";
    trajectoryBarsEl.appendChild(empty);
    return;
  }

  chartEl.classList.remove("empty-chart");
  const threshold = turns[0].lstm_threshold;
  timelineThresholdEl.style.top = `${Math.max(4, Math.min(94, (1 - threshold) * 100))}%`;

  turns.forEach((turn, index) => {
    const bar = document.createElement("button");
    bar.type = "button";
    bar.className = "timeline-bar";
    bar.dataset.turn = String(index);
    bar.dataset.score = turn.lstm_score.toFixed(3);
    bar.style.height = `${Math.max(4, Math.min(100, turn.lstm_score * 100))}%`;
    bar.classList.toggle("selected", index === selectedTurn);
    bar.classList.toggle("above", turn.lstm_score > turn.lstm_threshold);
    bar.setAttribute("aria-selected", String(index === selectedTurn));
    bar.setAttribute("aria-label", `Inspect turn ${index}, LSTM development score ${turn.lstm_score.toFixed(3)}`);
    bar.title = `Turn ${index}: ${turn.lstm_score.toFixed(3)}`;
    bar.addEventListener("click", () => renderPanelForTurn(index));
    trajectoryBarsEl.appendChild(bar);
  });
}

function renderPanelForTurn(turnIndex) {
  if (turnIndex === null || turnIndex < 0 || turnIndex >= turns.length) return;

  const turn = turns[turnIndex];
  const previous = turnIndex > 0 ? turns[turnIndex - 1] : null;
  const delta = previous ? turn.lstm_score - previous.lstm_score : null;
  const distance = turn.lstm_threshold - turn.lstm_score;

  selectedTurn = turnIndex;
  turnPillEl.textContent = `Turn ${turn.turn + 1} / ${turns.length} - Speaker ${turn.author === "user_A" ? "A" : "B"}`;
  riskEl.textContent = turn.risk_score.toFixed(3);
  lstmEl.textContent = turn.lstm_score.toFixed(3);
  scorePercentEl.textContent = `${(turn.lstm_score * 100).toFixed(1)}%`;
  lstmThresholdEl.textContent = turn.lstm_threshold.toFixed(3);
  weightedEl.textContent = turn.weighted_score.toFixed(3);
  weightedThresholdEl.textContent = turn.weighted_threshold.toFixed(3);
  sequenceLengthEl.textContent = `${turn.turn + 1} ${turn.turn === 0 ? "turn" : "turns"}`;
  thresholdDistanceEl.textContent = distance >= 0
    ? `${distance.toFixed(3)} below`
    : `${Math.abs(distance).toFixed(3)} above`;

  scoreFillEl.style.width = `${Math.max(0, Math.min(100, turn.lstm_score * 100))}%`;
  scoreFillEl.classList.toggle("above", turn.lstm_score > turn.lstm_threshold);
  thresholdMarkerEl.style.left = `${Math.max(0, Math.min(100, turn.lstm_threshold * 100))}%`;

  if (delta === null) {
    scoreDeltaEl.textContent = "First scored turn";
    scoreDeltaEl.classList.remove("rising", "falling");
  } else {
    scoreDeltaEl.textContent = `${delta >= 0 ? "+" : ""}${delta.toFixed(3)} from prior turn`;
    scoreDeltaEl.classList.toggle("rising", delta > 0);
    scoreDeltaEl.classList.toggle("falling", delta < 0);
  }

  setOutputState(turn);
  flagEl.textContent = turn.first_flagged_turn === null ? "None" : `Turn ${turn.first_flagged_turn + 1}`;
  crossingNoteEl.textContent = turn.first_flagged_turn === null
    ? "No development threshold crossing recorded"
    : "Historical model threshold - not a safety alert";

  renderFeatures(turn.trajectory_features);

  document.querySelectorAll(".message-row").forEach((row) => {
    const isSelected = Number.parseInt(row.dataset.turn, 10) === turnIndex;
    row.classList.toggle("selected", isSelected);
    row.setAttribute("aria-selected", String(isSelected));
  });
  renderTimeline();
}

function createScoreBadge(label, score, extraClass = "") {
  const badge = document.createElement("span");
  badge.className = `score-badge ${extraClass}`.trim();
  badge.textContent = `${label} ${score.toFixed(3)}`;
  return badge;
}

function appendMessage(data, timestamp) {
  emptyStateEl.classList.add("hidden");

  const row = document.createElement("li");
  row.className = `message-row ${data.author}`;
  row.dataset.turn = String(data.turn);
  row.setAttribute("aria-selected", "false");
  row.setAttribute("role", "button");
  row.tabIndex = 0;
  if (data.first_flagged_turn !== null && data.turn === data.first_flagged_turn) {
    row.classList.add("flagged-turn");
  }

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.textContent = data.author === "user_A" ? "A" : "B";

  const content = document.createElement("div");
  content.className = "message-content";
  const bubble = document.createElement("div");
  bubble.className = "message-bubble";

  const text = document.createElement("div");
  text.className = "message-text";
  text.textContent = data.text;

  const meta = document.createElement("div");
  meta.className = "message-meta";
  const identity = document.createElement("strong");
  identity.textContent = `Speaker ${data.author === "user_A" ? "A" : "B"}`;
  const turnLabel = document.createElement("span");
  turnLabel.textContent = `Turn ${data.turn + 1}`;
  const time = document.createElement("span");
  time.textContent = timestamp;
  meta.append(
    identity,
    turnLabel,
    time,
    createScoreBadge("L1", data.risk_score),
    createScoreBadge("LSTM", data.lstm_score, "score-badge-lstm"),
  );

  bubble.append(text, meta);
  if (data.first_flagged_turn !== null && data.turn === data.first_flagged_turn) {
    const marker = document.createElement("div");
    marker.className = "message-flag";
    marker.textContent = "First development-threshold crossing";
    bubble.appendChild(marker);
  }

  content.appendChild(bubble);
  row.append(avatar, content);
  row.addEventListener("click", () => renderPanelForTurn(Number.parseInt(row.dataset.turn, 10)));
  row.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      renderPanelForTurn(Number.parseInt(row.dataset.turn, 10));
    }
  });
  messagesEl.appendChild(row);
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
    `Historical development threshold first crossed at turn ${firstFlagged + 1}. ` +
    `Current LSTM score: ${lstmScore.toFixed(3)}. This is not a safety alert.`;
}

function updateComposerSpeaker() {
  const isSpeakerB = authorEl.value === "user_B";
  composerSpeakerEl.textContent = isSpeakerB ? "B" : "A";
  composerSpeakerEl.classList.toggle("speaker-b", isSpeakerB);
  composerAuthorLabelEl.textContent = isSpeakerB ? "Speaker B" : "Speaker A";
}

function setBusy(isBusy) {
  input.disabled = isBusy;
  authorEl.disabled = isBusy;
  sendBtn.disabled = isBusy;
  resetBtn.disabled = isBusy;
  sendBtn.querySelector("span:first-child").textContent = isBusy ? "Analyzing..." : "Analyze turn";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) {
    composerStatusEl.textContent = "Enter a message before analyzing the turn.";
    input.focus();
    return;
  }

  composerStatusEl.textContent = "";
  const author = authorEl.value;
  setBusy(true);

  try {
    await ensureConversation();
    const response = await fetch("/api/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conv_id: convId, text, author }),
    });
    const data = await readJsonOrThrow(response);

    turns.push(data);
    appendMessage(data, formatTimestamp(new Date()));
    updateBanner(data.first_flagged_turn, data.lstm_score);
    renderPanelForTurn(turns.length - 1);
    input.value = "";

    authorEl.value = author === "user_A" ? "user_B" : "user_A";
    updateComposerSpeaker();
  } catch (error) {
    composerStatusEl.textContent = error.message || "The turn could not be analyzed.";
  } finally {
    setBusy(false);
    input.focus();
  }
});

resetBtn.addEventListener("click", async () => {
  if (turns.length > 0 && !window.confirm("Clear this conversation and all displayed turn scores?")) {
    return;
  }
  resetBtn.disabled = true;
  composerStatusEl.textContent = "";
  try {
    if (convId) {
      const response = await fetch("/api/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ conv_id: convId }),
      });
      await readJsonOrThrow(response);
    }
  } catch (error) {
    composerStatusEl.textContent = error.message || "The conversation could not be cleared.";
    resetBtn.disabled = false;
    return;
  }

  convId = null;
  turns.length = 0;
  selectedTurn = null;
  messagesEl.innerHTML = "";
  emptyStateEl.classList.remove("hidden");
  featuresEl.innerHTML = '<p class="detail-empty">Select a scored turn to inspect its seven engineered signals.</p>';

  riskEl.textContent = "\u2014";
  lstmEl.textContent = "\u2014";
  lstmThresholdEl.textContent = "\u2014";
  thresholdDistanceEl.textContent = "\u2014";
  sequenceLengthEl.textContent = "0 turns";
  weightedEl.textContent = "\u2014";
  weightedThresholdEl.textContent = "\u2014";
  flagEl.textContent = "None";
  crossingNoteEl.textContent = "No development threshold crossing recorded";
  turnPillEl.textContent = "No turns yet";
  scoreDeltaEl.textContent = "\u2014";
  scorePercentEl.textContent = "\u2014";
  scoreFillEl.style.width = "0%";
  scoreFillEl.classList.remove("above");
  thresholdMarkerEl.style.left = "50%";
  outputStateEl.className = "output-state state-idle";
  outputStateLabelEl.textContent = "Waiting for input";

  bannerEl.classList.remove("active");
  bannerTextEl.textContent = "";
  renderTimeline();
  resetBtn.disabled = false;
  input.focus();
});

authorEl.addEventListener("change", updateComposerSpeaker);
updateComposerSpeaker();
renderTimeline();
