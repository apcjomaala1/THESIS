"use strict";

const scenarios = JSON.parse(document.getElementById("scenario-data").textContent);
const scenarioMap = new Map(scenarios.map((scenario) => [scenario.id, scenario]));

const scenarioSelect = document.getElementById("scenario-select");
const scenarioNote = document.getElementById("scenario-note");
const scenarioTarget = document.getElementById("scenario-target");
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
      <span class="message-score">Scoring…</span>
    </div>
    <p>${escapeHtml(text)}</p>`;
  messagesList.appendChild(item);
  item.scrollIntoView({ block: "nearest" });
  return item;
}

function updateMessage(item, turn, sanitizedText) {
  item.querySelector("p").textContent = sanitizedText;
  item.querySelector(".message-score").textContent =
    `Turn ${turn.turn} · T ${Number(turn.lstm_score).toFixed(4)} · E ${Number(turn.enhanced_lstm_score).toFixed(4)}`;
  item.classList.toggle("is-flagged", Boolean(turn.lstm_flagged || turn.enhanced_lstm_flagged));
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
  setActivity("Running both models…");

  try {
    const response = await fetch("/api/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ history: conversationHistory, model: "both" }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
    if (epoch !== conversationEpoch) return false;

    conversationHistory = data.sanitized_history;
    updateMessage(visibleMessage, data.latest_turn, conversationHistory.at(-1).text);
    updateResults(data);
    setActivity(`Scored turn ${data.turns_count}.`);
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

function setModelDecision(id, flagged) {
  const element = document.getElementById(id);
  element.textContent = flagged ? "Flagged" : "Below cutoff";
  element.className = `model-decision ${flagged ? "flagged" : "below"}`;
}

function updateResults(data) {
  const trajectory = data.decision.lstm;
  const embedding = data.decision.enhanced_lstm;
  const flaggedCount = Number(trajectory.flagged) + Number(embedding.flagged);
  const statusChip = document.getElementById("status-chip");

  statusChip.textContent = flaggedCount === 0 ? "Both below cutoff" : `${flaggedCount} of 2 flagged`;
  statusChip.className = `status-chip ${flaggedCount ? "status-flagged" : "status-below"}`;

  document.getElementById("lstm-score").textContent = Number(trajectory.score).toFixed(4);
  document.getElementById("enhanced-lstm-score").textContent = Number(embedding.score).toFixed(4);
  document.getElementById("score-fill").style.width = `${Math.max(0, Math.min(100, Number(trajectory.score) * 100))}%`;
  document.getElementById("embedding-score-fill").style.width = `${Math.max(0, Math.min(100, Number(embedding.score) * 100))}%`;
  setModelDecision("trajectory-decision", trajectory.flagged);
  setModelDecision("embedding-decision", embedding.flagged);

  document.getElementById("decision-text").textContent =
    `Turn ${data.turns_count}: Trajectory-Feature is ${trajectory.flagged ? "flagged" : "below cutoff"}; ` +
    `Embedding-and-Feature is ${embedding.flagged ? "flagged" : "below cutoff"}.`;
  updateOutcome(data);
}

function updateOutcome(data) {
  const outcomeCard = document.getElementById("outcome-card");
  const outcomeText = document.getElementById("outcome-text");
  const otherMethods = document.getElementById("other-methods");
  outcomeCard.className = "outcome-card";
  otherMethods.hidden = true;
  otherMethods.textContent = "";

  if (!activeScenario) {
    outcomeText.textContent = "Manual conversation: the models can score it, but no reference result is assigned.";
    return;
  }

  if (data.sanitized_history.length < activeScenario.turns.length) {
    outcomeText.textContent = `Turn ${data.turns_count} of ${activeScenario.turns.length}. Final decisions may still change.`;
    return;
  }

  const trajectoryFlagged = Boolean(data.decision.lstm.flagged);
  const embeddingFlagged = Boolean(data.decision.enhanced_lstm.flagged);
  const datasetExample = activeScenario.source?.kind === "pan12_validation";
  if (datasetExample) {
    const decisions = data.decision;
    const matchesRecord = Object.entries(activeScenario.expected_flags).every(
      ([method, expected]) => Boolean(decisions[method].flagged) === expected
    );
    outcomeCard.classList.add(matchesRecord ? "outcome-match" : "outcome-miss");
    outcomeText.textContent =
      `PAN12 validation reference: positive by listed predator-author membership. ` +
      `Final decisions: Trajectory-Feature ${trajectoryFlagged ? "flagged" : "below cutoff"}; ` +
      `Embedding-and-Feature ${embeddingFlagged ? "flagged" : "below cutoff"}.`;
    otherMethods.textContent =
      `Other methods: Weighted scorer ${decisions.weighted.flagged ? "flagged" : "below cutoff"}; ` +
      `Maximum Layer 1 ${decisions.raw_layer1.flagged ? "flagged" : "below cutoff"}; ` +
      `Keyword rule ${decisions.keyword.flagged ? "matched" : "no match"}.`;
    otherMethods.hidden = false;
    return;
  }

  const expected = Boolean(activeScenario.intended_review);
  const bothMatch = trajectoryFlagged === expected && embeddingFlagged === expected;
  outcomeCard.classList.add(bothMatch ? "outcome-match" : "outcome-miss");
  outcomeText.textContent =
    `Authored intent: ${expected ? "review" : "benign"}. ` +
    `Final decisions: Trajectory-Feature ${trajectoryFlagged ? "flagged" : "below cutoff"}; ` +
    `Embedding-and-Feature ${embeddingFlagged ? "flagged" : "below cutoff"}.`;
}

function resetConversation(message = "Ready.") {
  stopAutoplay();
  conversationEpoch += 1;
  requestQueue = Promise.resolve();
  scenarioStepIndex = 0;
  conversationHistory = [];
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
  document.getElementById("enhanced-lstm-score").textContent = "--";
  document.getElementById("score-fill").style.width = "0%";
  document.getElementById("embedding-score-fill").style.width = "0%";
  document.getElementById("decision-text").textContent = "Add a message to score the conversation.";
  for (const id of ["trajectory-decision", "embedding-decision"]) {
    const element = document.getElementById(id);
    element.textContent = "Waiting";
    element.className = "model-decision waiting";
  }
  const outcomeCard = document.getElementById("outcome-card");
  outcomeCard.className = "outcome-card";
  document.getElementById("outcome-text").textContent = activeScenario
    ? "Run the complete example to compare the final decisions with its reference."
    : "Manual conversation: the models can score it, but no reference result is assigned.";
  document.getElementById("other-methods").hidden = true;
  document.getElementById("other-methods").textContent = "";
}

function selectScenario(id) {
  activeScenario = scenarioMap.get(id) || null;
  const manual = !activeScenario;
  scenarioNote.textContent = manual
    ? "Enter alternating messages and watch both model decisions update after each turn."
    : activeScenario.short_note;
  scenarioTarget.textContent = manual
    ? "No reference result is assigned to manual input."
    : activeScenario.source?.kind === "pan12_validation"
      ? "PAN12 validation reference: a listed predator author participated. This is a conversation label, not a label for each message."
      : `Authored intent: ${activeScenario.intended_review ? "send for review" : "benign context"}.`;
  runButton.disabled = manual;
  stepButton.disabled = manual;
  speakerSelect.disabled = !manual;
  messageInput.disabled = !manual;
  document.getElementById("btn-send").disabled = !manual;
  resetConversation(manual ? "Manual entry is ready." : "Example loaded.");
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
    autoplayTimer = window.setTimeout(runAutoplayTurn, 450);
  } else {
    stopAutoplay();
  }
}

function stopAutoplay() {
  autoplayActive = false;
  if (autoplayTimer !== null) window.clearTimeout(autoplayTimer);
  autoplayTimer = null;
  runButton.textContent = "Run conversation";
}

function toggleAutoplay() {
  if (!activeScenario) return;
  if (autoplayActive) {
    stopAutoplay();
    setActivity("Example paused.");
    return;
  }
  if (scenarioStepIndex >= activeScenario.turns.length) resetConversation("Restarting example…");
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

selectScenario(scenarioSelect.value);
