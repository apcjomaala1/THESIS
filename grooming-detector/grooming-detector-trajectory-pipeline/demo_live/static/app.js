"use strict";

const scenarios = JSON.parse(document.getElementById("scenario-data").textContent);
const scenarioMap = new Map(scenarios.map((scenario) => [scenario.id, scenario]));
const lstmThreshold = Number(document.body.dataset.lstmThreshold);

const scenarioSelect = document.getElementById("scenario-select");
const scenarioNote = document.getElementById("scenario-note");
const runButton = document.getElementById("btn-autoplay");
const stepButton = document.getElementById("btn-step");
const resetButton = document.getElementById("btn-reset");
const composerForm = document.getElementById("composer-form");
const speakerSelect = document.getElementById("speaker-select");
const messageInput = document.getElementById("msg-input");
const activityText = document.getElementById("activity-text");
const emptyState = document.getElementById("chat-empty");
const messagesList = document.getElementById("messages-list");

let activeScenario = null;
let scenarioStepIndex = 0;
let conversationHistory = [];
let conversationEpoch = 0;
let requestQueue = Promise.resolve();
let autoplayActive = false;
let autoplayTimer = null;
let firstFlaggedTurn = null;

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function setActivity(message, isError = false) {
  activityText.textContent = message;
  activityText.classList.toggle("is-error", isError);
}

function appendMessage(author, text) {
  emptyState.hidden = true;
  const item = document.createElement("article");
  item.className = `message ${author === "user_A" ? "message-a" : "message-b"}`;
  item.innerHTML = `
    <div class="message-meta">
      <span>${author === "user_A" ? "Speaker A" : "Speaker B"}</span>
      <span class="message-score">Scoring...</span>
    </div>
    <p class="message-text">${escapeHtml(text)}</p>`;
  messagesList.appendChild(item);
  item.scrollIntoView({ block: "nearest" });
  return item;
}

function updateMessage(item, turn, sanitizedText) {
  item.querySelector(".message-text").textContent = sanitizedText;
  item.querySelector(".message-score").textContent =
    `Turn ${turn.turn} · L1 ${Number(turn.layer1_score).toFixed(4)} · LSTM ${Number(turn.lstm_score).toFixed(4)}`;
  item.classList.toggle("is-flagged", Boolean(turn.lstm_flagged));
}

function submitTurn(text, author) {
  const epoch = conversationEpoch;
  const task = requestQueue.then(() => submitTurnNow(text, author, epoch));
  requestQueue = task.catch(() => undefined);
  return task;
}

async function submitTurnNow(text, author, epoch) {
  const cleanText = String(text || "").trim();
  if (!cleanText || epoch !== conversationEpoch) return false;

  const visibleMessage = appendMessage(author, cleanText);
  conversationHistory.push({ author, text: cleanText });
  setActivity("Running the frozen model...");

  try {
    const response = await fetch("/api/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ history: conversationHistory }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
    if (epoch !== conversationEpoch) return false;

    conversationHistory = data.sanitized_history;
    const latest = data.latest_turn;
    updateMessage(visibleMessage, latest, conversationHistory.at(-1).text);
    updateResults(data);
    setActivity(`Scored ${data.turns_count} turn${data.turns_count === 1 ? "" : "s"}.`);
    return true;
  } catch (error) {
    if (epoch === conversationEpoch) {
      conversationHistory.pop();
      visibleMessage.remove();
      emptyState.hidden = messagesList.children.length > 0;
      setActivity(`Could not score that message: ${error.message}`, true);
    }
    return false;
  }
}

function firstTrueIndex(values) {
  const index = values.findIndex(Boolean);
  return index < 0 ? null : index + 1;
}

function updateResults(data) {
  const decision = data.decision;
  const latest = data.latest_turn;
  const score = Number(decision.lstm.score);
  firstFlaggedTurn = firstTrueIndex(data.trajectory_curve.lstm_flags);

  const statusChip = document.getElementById("status-chip");
  statusChip.textContent = decision.lstm.flagged ? "Flagged for review" : "Below threshold";
  statusChip.className = `status-chip ${decision.lstm.flagged ? "status-flagged" : "status-below"}`;
  document.getElementById("lstm-score").textContent = score.toFixed(4);
  document.getElementById("score-fill").style.width = `${Math.max(0, Math.min(100, score * 100))}%`;
  document.getElementById("decision-text").textContent = decision.lstm.flagged
    ? `The score crossed the frozen threshold of ${Number(decision.lstm.threshold).toFixed(4)}${firstFlaggedTurn ? ` at turn ${firstFlaggedTurn}` : ""}. Send this conversation for human review.`
    : `The score is below the frozen threshold of ${Number(decision.lstm.threshold).toFixed(4)}. This is not a declaration that the chat is safe.`;

  document.getElementById("latest-turn-label").textContent = `turn ${latest.turn} · ${latest.author === "user_A" ? "Speaker A" : "Speaker B"}`;
  const features = latest.features;
  setValue("val-peak", features.peak_proxy_score);
  setValue("val-current", features.current_proxy_score);
  setValue("val-spikes", features.spike_count, 0);
  setValue("val-drop", features.spike_then_drop ? "yes" : "no", null);
  setValue("val-rate", features.rate_of_change);
  setValue("val-topic", features.topic_distance);
  setValue("val-imbalance", features.turn_taking_imbalance);
  document.getElementById("context-box").textContent = latest.context;

  updateComparison(data);
  drawTrajectory(data.trajectory_curve);
}

function setValue(id, value, digits = 4) {
  document.getElementById(id).textContent = digits === null ? String(value) : Number(value).toFixed(digits);
}

const comparisonMethods = [
  ["lstm", "Primary LSTM"],
  ["weighted", "Weighted scorer"],
  ["raw_layer1", "Maximum Layer 1"],
  ["keyword", "Keyword rule"],
];

function updateComparison(data) {
  const complete = Boolean(data && activeScenario &&
    data.sanitized_history.length === activeScenario.turns.length &&
    data.sanitized_history.every((turn, i) =>
      turn.author === activeScenario.turns[i].author && turn.text === activeScenario.turns[i].text));
  const datasetExample = activeScenario?.source?.kind === "pan12_validation";
  const referenceLabel = datasetExample ? Boolean(activeScenario.source.reference_label) : activeScenario?.intended_review;
  const target = complete ? referenceLabel : null;
  const body = document.getElementById("comparison-body");
  body.replaceChildren();
  for (const [key, label] of comparisonMethods) {
    const item = data?.decision[key];
    const row = document.createElement("tr");
    const correct = target !== null && item && item.flagged === target;
    if (target !== null && item) row.className = correct ? "outcome-correct" : "outcome-error";
    const title = document.createElement("th");
    title.scope = "row";
    title.textContent = label;
    row.appendChild(title);
    const score = !item ? "--" : key === "keyword"
      ? (item.matched_terms.length ? `Match: ${item.matched_terms.join(", ")}` : "No term matched")
      : `${Number(item.score).toFixed(4)} / ${Number(item.threshold).toFixed(4)}`;
    const outcome = target === null ? (data ? "No reference label" : "--")
      : target ? (item.flagged ? "TP: caught" : "FN: missed")
      : (item.flagged ? "FP: false alarm" : "TN: below threshold");
    for (const text of [score, !item ? "Waiting" : item.flagged ? "Flagged" : "Below threshold", outcome]) {
      const cell = document.createElement("td");
      cell.textContent = text;
      row.appendChild(cell);
    }
    body.appendChild(row);
  }
  let summary = "Run the full chat to compare the final decisions.";
  if (data && !activeScenario) {
    summary = "Manual input: decisions can be compared, but FP/FN cannot be assigned without a reference label.";
  } else if (data && !complete) {
    summary = `Prefix ${data.turns_count} of ${activeScenario.turns.length}: decisions may change. FP/FN labels appear after the full chat.`;
  } else if (complete) {
    const lstm = data.decision.lstm;
    const corrected = comparisonMethods.filter(([key]) => key !== "lstm" &&
      lstm.flagged === target && data.decision[key].flagged !== target).map(([, label]) => label);
    const positiveDescription = datasetExample ? "dataset-positive conversation" : "intended review case";
    const negativeDescription = datasetExample ? "dataset-negative conversation" : "benign example";
    if (corrected.length) {
      summary = target
        ? `Miss caught: the LSTM flags this ${positiveDescription}; ${corrected.join(" and ")} ${corrected.length === 1 ? "misses" : "miss"} it.`
        : `False alarm avoided at the end: the LSTM is below threshold for this ${negativeDescription}; ${corrected.join(" and ")} ${corrected.length === 1 ? "flags" : "flag"} it.`;
    } else if (lstm.flagged !== target) {
      summary = target ? `Limitation: the LSTM misses this ${positiveDescription}.` : `Limitation: the LSTM flags this ${negativeDescription}.`;
    } else {
      summary = "The methods agree on this example; it does not demonstrate an advantage.";
    }
    if (!target && data.trajectory_curve.lstm_flags.some(Boolean)) {
      summary += " The LSTM also flagged an earlier prefix; this is a final-conversation correction.";
    }
  }
  document.getElementById("comparison-summary").textContent = summary;
}

function drawTrajectory(curve) {
  const scores = curve.lstm_scores.map(Number);
  const xAt = (index) => scores.length === 1 ? 260 : 16 + (488 * index) / (scores.length - 1);
  const yAt = (score) => 126 - 110 * Math.max(0, Math.min(1, score));
  const path = scores.map((score, index) => `${index ? "L" : "M"} ${xAt(index).toFixed(1)} ${yAt(score).toFixed(1)}`).join(" ");
  document.getElementById("path-lstm").setAttribute("d", path);

  const points = document.getElementById("chart-points");
  points.replaceChildren();
  scores.forEach((score, index) => {
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", xAt(index));
    circle.setAttribute("cy", yAt(score));
    circle.setAttribute("r", "4");
    circle.setAttribute("class", curve.lstm_flags[index] ? "chart-point flagged" : "chart-point");
    points.appendChild(circle);
  });
}

function resetConversation(message = "Ready. Messages are scored locally on this computer.") {
  stopAutoplay();
  conversationEpoch += 1;
  requestQueue = Promise.resolve();
  scenarioStepIndex = 0;
  conversationHistory = [];
  firstFlaggedTurn = null;
  messagesList.replaceChildren();
  emptyState.hidden = false;
  resetResults();
  setActivity(message);
}

function resetResults() {
  const statusChip = document.getElementById("status-chip");
  statusChip.textContent = "Waiting";
  statusChip.className = "status-chip status-waiting";
  document.getElementById("lstm-score").textContent = "--";
  document.getElementById("score-fill").style.width = "0%";
  document.getElementById("decision-text").textContent = "Add a message to run DistilBERT and the LSTM.";
  document.getElementById("latest-turn-label").textContent = "no turn yet";
  ["val-peak", "val-current", "val-spikes", "val-drop", "val-rate", "val-topic", "val-imbalance"].forEach((id) => {
    document.getElementById(id).textContent = "--";
  });
  document.getElementById("context-box").textContent = "No context yet.";
  document.getElementById("path-lstm").setAttribute("d", "");
  document.getElementById("chart-points").replaceChildren();
  updateComparison(null);
}

function selectScenario(id) {
  activeScenario = scenarioMap.get(id) || null;
  const manual = !activeScenario;
  scenarioNote.textContent = manual
    ? "Enter alternating messages below. Each submission recomputes the full conversation history."
    : activeScenario.short_note;
  runButton.disabled = manual;
  stepButton.disabled = manual;
  speakerSelect.disabled = !manual;
  messageInput.disabled = !manual;
  document.getElementById("btn-send").disabled = !manual;
  const datasetExample = activeScenario?.source?.kind === "pan12_validation";
  document.getElementById("scenario-target").textContent = manual
    ? "Manual conversation: no reference label; correctness cannot be assigned."
    : datasetExample
      ? `Source: PAN12 validation | ${activeScenario.source.conversation_id} | Reference label ${activeScenario.source.reference_label}: ${activeScenario.source.reference_label ? "contains a listed predator author" : "contains no listed predator author"}. This is a conversation-level label, not a label for each message.`
      : `Authored intent: ${activeScenario.intended_review ? "requires review" : "benign context"}. Synthetic illustration, not an evaluation record.`;
  resetConversation(manual ? "Manual entry is ready." : "Example loaded. Run it all at once or add one message at a time.");
  if (manual) messageInput.focus();
}

async function stepScenarioTurn() {
  if (!activeScenario || scenarioStepIndex >= activeScenario.turns.length) return false;
  const turn = activeScenario.turns[scenarioStepIndex];
  const succeeded = await submitTurn(turn.text, turn.author);
  if (succeeded) scenarioStepIndex += 1;
  if (scenarioStepIndex >= activeScenario.turns.length) {
    stopAutoplay();
    setActivity(`Example complete: ${activeScenario.turns.length} turns scored.`);
  }
  return succeeded;
}

async function runAutoplayTurn() {
  if (!autoplayActive) return;
  const succeeded = await stepScenarioTurn();
  if (autoplayActive && succeeded && activeScenario && scenarioStepIndex < activeScenario.turns.length) {
    autoplayTimer = window.setTimeout(runAutoplayTurn, 600);
  } else {
    stopAutoplay();
  }
}

function stopAutoplay() {
  autoplayActive = false;
  if (autoplayTimer !== null) window.clearTimeout(autoplayTimer);
  autoplayTimer = null;
  runButton.textContent = "Run full chat";
}

function toggleAutoplay() {
  if (!activeScenario) return;
  if (autoplayActive) {
    stopAutoplay();
    setActivity("Example paused.");
    return;
  }
  if (scenarioStepIndex >= activeScenario.turns.length) resetConversation("Restarting example...");
  autoplayActive = true;
  runButton.textContent = "Pause";
  runAutoplayTurn();
}

composerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) return;
  const author = speakerSelect.value;
  messageInput.value = "";
  const succeeded = await submitTurn(text, author);
  if (succeeded) speakerSelect.value = author === "user_A" ? "user_B" : "user_A";
  messageInput.focus();
});

scenarioSelect.addEventListener("change", () => selectScenario(scenarioSelect.value));
runButton.addEventListener("click", toggleAutoplay);
stepButton.addEventListener("click", stepScenarioTurn);
resetButton.addEventListener("click", () => resetConversation());

const thresholdY = 126 - 110 * Math.max(0, Math.min(1, lstmThreshold));
document.getElementById("chart-threshold").setAttribute("y1", thresholdY);
document.getElementById("chart-threshold").setAttribute("y2", thresholdY);
selectScenario(scenarioSelect.value);
