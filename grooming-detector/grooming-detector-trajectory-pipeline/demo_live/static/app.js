/**
 * PAN12 Conversation Trajectory Benchmark - Frontend Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  // State
  let currentSpeaker = "user_A"; // "user_A" (Speaker A) or "user_B" (Speaker B)
  let conversationHistory = [];
  let scenarios = [];
  let activeScenario = null;
  let scenarioStepIndex = 0;
  let autoPlayTimer = null;
  let autoPlayActive = false;
  let firstCrossedTurn = null;
  let conversationEpoch = 0;
  let requestQueue = Promise.resolve();

  // DOM Elements
  const msgInput = document.getElementById("msg-input");
  const composerForm = document.getElementById("composer-form");
  const btnToggleSpeaker = document.getElementById("btn-toggle-speaker");
  const currentSpeakerAvatar = document.getElementById("current-speaker-avatar");
  const currentSpeakerLabel = document.getElementById("current-speaker-label");
  const messagesList = document.getElementById("messages-list");
  const chatEmpty = document.getElementById("chat-empty");
  const chatWindow = document.getElementById("chat-window");

  // Scenario Elements
  const scenarioChips = document.getElementById("scenario-chips");
  const infoBadge = document.getElementById("info-badge");
  const infoTitle = document.getElementById("info-title");
  const infoDesc = document.getElementById("info-desc");
  const btnAutoPlay = document.getElementById("btn-autoplay");
  const btnStep = document.getElementById("btn-step");
  const btnReset = document.getElementById("btn-reset");

  // Dashboard Elements
  const gaugeFill = document.getElementById("gauge-fill");
  const gaugePct = document.getElementById("gauge-pct");
  const statusBadge = document.getElementById("status-badge");
  const statusText = document.getElementById("status-text");
  const decisionDesc = document.getElementById("decision-desc");
  const prefixCrossing = document.getElementById("prefix-crossing");
  const flagTurnNum = document.getElementById("flag-turn-num");

  // Signals
  const valPeak = document.getElementById("val-peak");
  const barPeak = document.getElementById("bar-peak");
  const valCurr = document.getElementById("val-curr");
  const barCurr = document.getElementById("bar-curr");
  const valSpikes = document.getElementById("val-spikes");
  const barSpikes = document.getElementById("bar-spikes");
  const valDrop = document.getElementById("val-drop");
  const barDrop = document.getElementById("bar-drop");
  const valRate = document.getElementById("val-rate");
  const barRate = document.getElementById("bar-rate");
  const valTopic = document.getElementById("val-topic");
  const barTopic = document.getElementById("bar-topic");
  const valImbalance = document.getElementById("val-imbalance");
  const barImbalance = document.getElementById("bar-imbalance");

  // Comparators
  const compLstmScore = document.getElementById("comp-lstm-score");
  const compLstmFlag = document.getElementById("comp-lstm-flag");
  const compWeightedScore = document.getElementById("comp-weighted-score");
  const compWeightedFlag = document.getElementById("comp-weighted-flag");
  const compRawScore = document.getElementById("comp-raw-score");
  const compRawFlag = document.getElementById("comp-raw-flag");
  const compKeywordScore = document.getElementById("comp-keyword-score");
  const compKeywordFlag = document.getElementById("comp-keyword-flag");

  // Context Box
  const contextBox = document.getElementById("context-box");

  // Trajectory Chart SVG Paths
  const pathLstm = document.getElementById("path-lstm");
  const pathL1 = document.getElementById("path-l1");
  const pathTopic = document.getElementById("path-topic");
  const chartPoints = document.getElementById("chart-points");

  // 1. Load Scenarios from API
  fetch("/api/scenarios")
    .then((r) => r.json())
    .then((data) => {
      scenarios = data;
      if (scenarios.length > 0) {
        selectScenario(scenarios[0]);
      }
    })
    .catch((err) => console.error("Error loading scenarios:", err));

  // 2. Speaker Toggle Logic
  function setSpeaker(speaker) {
    currentSpeaker = speaker;
    if (speaker === "user_A") {
      currentSpeakerAvatar.className = "speaker-pill pill-a active";
      currentSpeakerAvatar.textContent = "A";
      currentSpeakerLabel.textContent = "Speaker A (Initiator)";
    } else {
      currentSpeakerAvatar.className = "speaker-pill pill-b active";
      currentSpeakerAvatar.textContent = "B";
      currentSpeakerLabel.textContent = "Speaker B";
    }
  }

  btnToggleSpeaker.addEventListener("click", () => {
    setSpeaker(currentSpeaker === "user_A" ? "user_B" : "user_A");
  });

  // Global Tab key to switch speaker when focused on input
  document.addEventListener("keydown", (e) => {
    if (e.key === "Tab" && document.activeElement === msgInput) {
      e.preventDefault();
      setSpeaker(currentSpeaker === "user_A" ? "user_B" : "user_A");
    }
  });

  // 3. Scenario Selection
  function selectScenario(sc) {
    stopAutoPlay();
    activeScenario = sc;
    scenarioStepIndex = 0;
    resetConversation();

    // Update tab states
    document.querySelectorAll(".scenario-tab").forEach((tab) => {
      tab.classList.toggle("tab-active", tab.dataset.id === sc.id);
    });

    if (sc.id === "custom") {
      infoBadge.textContent = "Custom Mode";
      infoBadge.className = "meta-badge badge-neutral";
      infoTitle.textContent = "Custom Synthetic Conversation Transcript";
      infoDesc.textContent = "Enter messages below to inspect how the frozen Layer 1 DistilBERT author-proxy and Layer 2 LSTM respond to the chronological prefix.";
      btnAutoPlay.style.display = "none";
      btnStep.style.display = "none";
    } else {
      infoBadge.textContent = sc.badge;
      infoBadge.className = `meta-badge ${sc.badge_class}`;
      infoTitle.textContent = sc.title;
      infoDesc.textContent = sc.description;
      btnAutoPlay.style.display = "inline-flex";
      btnStep.style.display = "inline-flex";
    }
  }

  scenarioChips.addEventListener("click", (e) => {
    const tab = e.target.closest(".scenario-tab");
    if (!tab) return;
    const id = tab.dataset.id;
    if (id === "custom") {
      selectScenario({ id: "custom" });
    } else {
      const found = scenarios.find((s) => s.id === id);
      if (found) selectScenario(found);
    }
  });

  // 4. Send Message & Score
  async function submitTurnNow(text, author, epoch) {
    if (!text || !text.trim()) return;
    if (epoch !== conversationEpoch) return;

    // Add to history
    conversationHistory.push({ author: author, text: text.trim() });
    const turnIndex = conversationHistory.length;

    // Append to UI immediately
    chatEmpty.style.display = "none";
    const row = document.createElement("div");
    row.className = `transcript-row ${author === "user_A" ? "row-speaker-a" : "row-speaker-b"}`;
    row.id = `turn-row-${turnIndex}`;
    row.innerHTML = `
      <div class="turn-header">
        <div class="turn-speaker-group">
          <span class="speaker-tag ${author === "user_A" ? "tag-a" : "tag-b"}">
            ${author === "user_A" ? "Speaker A" : "Speaker B"}
          </span>
          <span class="turn-index">Turn #${turnIndex}</span>
        </div>
        <span class="turn-metric" id="score-tag-${turnIndex}">Evaluating...</span>
      </div>
      <div class="turn-text">${escapeHtml(text)}</div>
    `;
    messagesList.appendChild(row);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // Alternate speaker for the next turn
    setSpeaker(author === "user_A" ? "user_B" : "user_A");

    // Call scoring API
    try {
      const res = await fetch("/api/score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ history: conversationHistory }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Scoring failed");
      if (epoch !== conversationEpoch) return;
      if (Array.isArray(data.sanitized_history)) {
        conversationHistory = data.sanitized_history;
        const sanitizedText = conversationHistory[conversationHistory.length - 1].text;
        const visibleText = row.querySelector(".turn-text");
        if (visibleText) visibleText.textContent = sanitizedText;
      }
      updateDashboard(data);
    } catch (err) {
      console.error("Error scoring turn:", err);
    }
  }

  function submitTurn(text, author) {
    const epoch = conversationEpoch;
    const queuedRequest = requestQueue.then(() => submitTurnNow(text, author, epoch));
    requestQueue = queuedRequest.catch((err) => {
      console.error("Queued scoring error:", err);
    });
    return queuedRequest;
  }

  composerForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = msgInput.value;
    msgInput.value = "";
    submitTurn(text, currentSpeaker);
    msgInput.focus();
  });

  // 5. Auto-Play & Stepper Logic
  function stepNextTurn() {
    if (!activeScenario || !activeScenario.turns) return;
    if (scenarioStepIndex >= activeScenario.turns.length) {
      stopAutoPlay();
      return;
    }
    const turn = activeScenario.turns[scenarioStepIndex];
    scenarioStepIndex++;
    return submitTurn(turn.text, turn.author);
  }

  async function runAutoPlayTurn() {
    if (!autoPlayActive) return;
    if (!activeScenario || scenarioStepIndex >= activeScenario.turns.length) {
      stopAutoPlay();
      return;
    }
    await stepNextTurn();
    if (!autoPlayActive) return;
    if (scenarioStepIndex >= activeScenario.turns.length) {
      stopAutoPlay();
      return;
    }
    autoPlayTimer = setTimeout(runAutoPlayTurn, 1400);
  }

  function startAutoPlay() {
    if (autoPlayActive) return;
    autoPlayActive = true;
    btnAutoPlay.textContent = "Pause Auto-Play";
    btnAutoPlay.className = "btn btn-secondary btn-sm";
    runAutoPlayTurn();
  }

  function stopAutoPlay() {
    autoPlayActive = false;
    if (autoPlayTimer) {
      clearTimeout(autoPlayTimer);
      autoPlayTimer = null;
    }
    btnAutoPlay.textContent = "Auto-Play Scenario";
    btnAutoPlay.className = "btn btn-primary btn-sm";
  }

  btnAutoPlay.addEventListener("click", () => {
    if (autoPlayActive) stopAutoPlay();
    else startAutoPlay();
  });

  btnStep.addEventListener("click", () => {
    stopAutoPlay();
    stepNextTurn();
  });

  btnReset.addEventListener("click", () => {
    stopAutoPlay();
    resetConversation();
  });

  function resetConversation() {
    conversationEpoch += 1;
    conversationHistory = [];
    scenarioStepIndex = 0;
    firstCrossedTurn = null;
    messagesList.innerHTML = "";
    chatEmpty.style.display = "flex";
    setSpeaker("user_A");
    resetDashboard();
  }

  // 6. Dashboard Updates
  function updateDashboard(data) {
    const latest = data.latest_turn;
    const decision = data.decision;
    const curve = data.trajectory_curve;

    // Update Turn Score Tag
    const scoreTag = document.getElementById(`score-tag-${data.turns_count}`);
    if (scoreTag) {
      scoreTag.textContent = `L1: ${latest.layer1_score.toFixed(4)}`;
      if (latest.proxy_spike) {
        scoreTag.className = "turn-metric metric-spike";
        scoreTag.textContent = `L1: ${latest.layer1_score.toFixed(4)} (Spike)`;
      } else {
        scoreTag.className = "turn-metric";
      }
    }

    // A. Update Linear Meter & Score Readout
    const lstmScore = decision.lstm.score;
    gaugePct.textContent = lstmScore.toFixed(4);
    gaugeFill.style.width = `${Math.min(100, Math.max(0, lstmScore * 100))}%`;

    if (decision.lstm.flagged) {
      gaugeFill.style.backgroundColor = "var(--status-flagged)";
      statusBadge.className = "status-badge badge-danger-live";
      statusText.textContent = "FLAGGED FOR REVIEW";
      decisionDesc.textContent = `Current-prefix score (${lstmScore.toFixed(4)}) meets or exceeds the frozen decision threshold (${decision.lstm.threshold.toFixed(4)}). Route conversation for human review.`;

      if (!firstCrossedTurn) {
        firstCrossedTurn = data.turns_count;
        prefixCrossing.style.display = "inline-block";
        flagTurnNum.textContent = firstCrossedTurn;
      }
    } else {
      gaugeFill.style.backgroundColor = "var(--accent-blue)";
      statusBadge.className = "status-badge badge-below-live";
      statusText.textContent = "NOMINAL (BELOW THRESHOLD)";
      decisionDesc.textContent = `Current-prefix score (${lstmScore.toFixed(4)}) remains below the frozen decision threshold (${decision.lstm.threshold.toFixed(4)}).`;
    }

    // B. Update 7 Signals
    const f = latest.features;
    valPeak.textContent = f.peak_proxy_score.toFixed(4);
    barPeak.style.width = `${Math.min(100, f.peak_proxy_score * 100)}%`;

    valCurr.textContent = f.current_proxy_score.toFixed(4);
    barCurr.style.width = `${Math.min(100, f.current_proxy_score * 100)}%`;

    valSpikes.textContent = f.spike_count;
    barSpikes.style.width = `${Math.min(100, f.spike_count * 25)}%`;

    valDrop.textContent = f.spike_then_drop ? "True" : "False";
    barDrop.style.width = f.spike_then_drop ? "100%" : "0%";

    valRate.textContent = (f.rate_of_change >= 0 ? "+" : "") + f.rate_of_change.toFixed(4);
    barRate.style.width = `${Math.max(0, Math.min(100, 50 + (f.rate_of_change * 50)))}%`;

    valTopic.textContent = f.topic_distance.toFixed(4);
    barTopic.style.width = `${Math.min(100, f.topic_distance * 50)}%`;

    valImbalance.textContent = f.turn_taking_imbalance.toFixed(4);
    barImbalance.style.width = `${Math.min(100, f.turn_taking_imbalance * 100)}%`;

    // C. Update Comparators Table
    compLstmScore.textContent = decision.lstm.score.toFixed(4);
    compLstmFlag.innerHTML = decision.lstm.flagged
      ? '<span class="table-badge badge-flagged">Flagged</span>'
      : '<span class="table-badge badge-nominal">Nominal</span>';

    compWeightedScore.textContent = decision.weighted.score.toFixed(4);
    compWeightedFlag.innerHTML = decision.weighted.flagged
      ? '<span class="table-badge badge-flagged">Flagged</span>'
      : '<span class="table-badge badge-nominal">Nominal</span>';

    compRawScore.textContent = decision.raw_layer1.score.toFixed(4);
    compRawFlag.innerHTML = decision.raw_layer1.flagged
      ? '<span class="table-badge badge-flagged">Flagged</span>'
      : '<span class="table-badge badge-nominal">Nominal</span>';

    const matchedTerms = decision.keyword.matched_terms || [];
    compKeywordScore.textContent = decision.keyword.flagged
      ? `${matchedTerms.length} hit${matchedTerms.length === 1 ? "" : "s"}`
      : "No hit";
    compKeywordFlag.innerHTML = decision.keyword.flagged
      ? '<span class="table-badge badge-flagged">Flagged</span>'
      : '<span class="table-badge badge-nominal">Nominal</span>';

    // D. Update Context Box
    contextBox.textContent = latest.context || "[No context available]";

    // E. Render Trajectory Chart (SVG)
    renderTrajectoryChart(curve);
  }

  function resetDashboard() {
    gaugePct.textContent = "0.0000";
    gaugeFill.style.width = "0%";
    gaugeFill.style.backgroundColor = "var(--accent-blue)";
    statusBadge.className = "status-badge badge-neutral";
    statusText.textContent = "AWAITING INPUT";
    decisionDesc.textContent = "Awaiting initial turn. Prefix scores are evaluated sequentially against the frozen decision boundary.";
    prefixCrossing.style.display = "none";

    valPeak.textContent = "0.0000";
    barPeak.style.width = "0%";
    valCurr.textContent = "0.0000";
    barCurr.style.width = "0%";
    valSpikes.textContent = "0";
    barSpikes.style.width = "0%";
    valDrop.textContent = "False";
    barDrop.style.width = "0%";
    valRate.textContent = "0.0000";
    barRate.style.width = "50%";
    valTopic.textContent = "0.0000";
    barTopic.style.width = "0%";
    valImbalance.textContent = "0.0000";
    barImbalance.style.width = "0%";

    compLstmScore.textContent = "0.0000";
    compLstmFlag.innerHTML = '<span class="table-badge badge-below">Nominal</span>';
    compWeightedScore.textContent = "0.0000";
    compWeightedFlag.innerHTML = '<span class="table-badge badge-below">Nominal</span>';
    compRawScore.textContent = "0.0000";
    compRawFlag.innerHTML = '<span class="table-badge badge-below">Nominal</span>';
    compKeywordScore.textContent = "No hit";
    compKeywordFlag.innerHTML = '<span class="table-badge badge-below">Nominal</span>';

    contextBox.textContent = "[Awaiting conversation messages...]";

    pathLstm.setAttribute("d", "");
    pathL1.setAttribute("d", "");
    pathTopic.setAttribute("d", "");
    chartPoints.innerHTML = "";
  }

  // 7. Trajectory SVG Chart Renderer
  function renderTrajectoryChart(curve) {
    const turns = curve.turns;
    const N = turns.length;
    if (N === 0) return;

    const width = 500;
    const height = 160;
    const padTop = 15;
    const padBottom = 15;
    const padLeft = 15;
    const padRight = 15;

    const plotW = width - padLeft - padRight;
    const plotH = height - padTop - padBottom;

    function getX(i) {
      if (N === 1) return padLeft + plotW / 2;
      return padLeft + (i / (N - 1)) * plotW;
    }

    function getY(val, scaleMax = 1) {
      const normalized = Math.max(0, Math.min(1, val / scaleMax));
      return height - padBottom - (normalized * plotH);
    }

    function buildPath(values, scaleMax = 1) {
      let d = "";
      values.forEach((v, i) => {
        const x = getX(i);
        const y = getY(v, scaleMax);
        d += (i === 0 ? `M ${x} ${y}` : ` L ${x} ${y}`);
      });
      return d;
    }

    pathLstm.setAttribute("d", buildPath(curve.lstm_scores));
    pathL1.setAttribute("d", buildPath(curve.layer1_scores));
    pathTopic.setAttribute("d", buildPath(curve.topic_distances, 2));

    // Render points on the LSTM path
    let pointsHtml = "";
    curve.lstm_scores.forEach((s, i) => {
      const x = getX(i);
      const y = getY(s);
      const isFlagged = Boolean(curve.lstm_flags[i]);
      pointsHtml += `
        <circle cx="${x}" cy="${y}" r="${isFlagged ? 4 : 3}"
                fill="${isFlagged ? '#ef4444' : '#3b82f6'}"
                stroke="#0c1017" stroke-width="1.5">
          <title>Turn ${i + 1}: LSTM = ${s.toFixed(4)}</title>
        </circle>
      `;
    });
    chartPoints.innerHTML = pointsHtml;
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
