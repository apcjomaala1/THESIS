/** End-to-end DOM smoke test for the local demo using installed Microsoft Edge. */

import { spawn } from "node:child_process";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";

const EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const DEMO_URL = process.env.WASD_DEMO_URL || "http://127.0.0.1:5000/";
const DEBUG_PORT = 9333;
const profile = await mkdtemp(path.join(tmpdir(), "wasd-demo-edge-"));
const edge = spawn(EDGE, [
  "--headless=new",
  `--remote-debugging-port=${DEBUG_PORT}`,
  `--user-data-dir=${profile}`,
  "--no-first-run",
  "--disable-gpu",
  "--disable-breakpad",
  "--disable-crash-reporter",
  "about:blank",
], { stdio: "ignore", windowsHide: true });

const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

async function retry(action, timeout = 20000) {
  const deadline = Date.now() + timeout;
  let lastError;
  while (Date.now() < deadline) {
    try {
      const value = await action();
      if (value) return value;
    } catch (error) {
      lastError = error;
    }
    await delay(150);
  }
  throw lastError || new Error("Timed out waiting for browser state");
}

async function connectCdp() {
  const pages = await retry(async () => {
    const response = await fetch(`http://127.0.0.1:${DEBUG_PORT}/json/list`);
    return response.ok ? response.json() : null;
  });
  const target = pages.find((page) => page.type === "page");
  if (!target) throw new Error("Edge did not expose a page target");

  const socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    socket.addEventListener("open", resolve, { once: true });
    socket.addEventListener("error", reject, { once: true });
  });

  let sequence = 0;
  const pending = new Map();
  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (!message.id || !pending.has(message.id)) return;
    const { resolve, reject } = pending.get(message.id);
    pending.delete(message.id);
    if (message.error) reject(new Error(message.error.message));
    else resolve(message.result);
  });

  const call = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++sequence;
    pending.set(id, { resolve, reject });
    socket.send(JSON.stringify({ id, method, params }));
  });
  return { socket, call };
}

let cdp;
try {
  cdp = await connectCdp();
  await cdp.call("Page.enable");
  await cdp.call("Runtime.enable");
  await cdp.call("Emulation.setDeviceMetricsOverride", {
    width: 1440,
    height: 1050,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await cdp.call("Page.navigate", { url: DEMO_URL });

  async function evaluate(expression) {
    const response = await cdp.call("Runtime.evaluate", {
      expression,
      awaitPromise: true,
      returnByValue: true,
    });
    if (response.exceptionDetails) throw new Error(response.exceptionDetails.text);
    return response.result.value;
  }

  async function waitFor(expression, timeout = 60000) {
    return retry(() => evaluate(expression), timeout);
  }

  async function snapshot() {
    return evaluate(`({
      title: document.title,
      heading: document.querySelector("h1")?.textContent,
      messages: document.querySelectorAll(".message").length,
      status: document.getElementById("status-chip")?.textContent,
      score: document.getElementById("lstm-score")?.textContent,
      activity: document.getElementById("activity-text")?.textContent
    })`);
  }

  await waitFor(`document.getElementById("btn-autoplay") !== null`);
  const initial = await snapshot();

  await evaluate(`document.getElementById("btn-autoplay").click()`);
  await waitFor(`document.getElementById("activity-text").textContent.startsWith("Example complete")`);
  const flagged = await snapshot();
  let screenshot = null;
  if (process.env.WASD_DEMO_SCREENSHOT) {
    screenshot = path.resolve(process.env.WASD_DEMO_SCREENSHOT);
    await mkdir(path.dirname(screenshot), { recursive: true });
    const capture = await cdp.call("Page.captureScreenshot", {
      format: "png",
      fromSurface: true,
      captureBeyondViewport: true,
    });
    await writeFile(screenshot, Buffer.from(capture.data, "base64"));
  }

  await evaluate(`(() => {
    const select = document.getElementById("scenario-select");
    select.value = "routine_project_chat";
    select.dispatchEvent(new Event("change", { bubbles: true }));
    document.getElementById("btn-autoplay").click();
    return true;
  })()`);
  await waitFor(`document.getElementById("activity-text").textContent.startsWith("Example complete")`);
  const routine = await snapshot();

  await evaluate(`(() => {
    const select = document.getElementById("scenario-select");
    select.value = "concerning_but_below";
    select.dispatchEvent(new Event("change", { bubbles: true }));
    document.getElementById("btn-step").click();
    return true;
  })()`);
  await waitFor(`document.querySelectorAll(".message").length === 1 && document.getElementById("activity-text").textContent.startsWith("Scored")`);
  const limitationStep = await snapshot();
  await evaluate(`document.getElementById("btn-autoplay").click()`);
  await waitFor(`document.getElementById("activity-text").textContent.startsWith("Example complete")`);
  const limitation = await snapshot();

  await evaluate(`(() => {
    const select = document.getElementById("scenario-select");
    select.value = "custom";
    select.dispatchEvent(new Event("change", { bubbles: true }));
    document.getElementById("msg-input").value = "Can you check my draft after lunch?";
    document.getElementById("btn-send").click();
    return true;
  })()`);
  await waitFor(`document.querySelectorAll(".message").length === 1 && document.getElementById("activity-text").textContent.startsWith("Scored")`);
  const manual = await snapshot();

  await evaluate(`document.getElementById("btn-reset").click()`);
  await waitFor(`document.querySelectorAll(".message").length === 0`);
  const cleared = await snapshot();

  const checks = {
    initial_loaded: initial.title === "Conversation Model Demo" && initial.status === "Waiting",
    flagged_example: flagged.messages === 6 && flagged.status === "Flagged for review" && flagged.score === "0.9942",
    routine_example: routine.messages === 6 && routine.status === "Below threshold" && routine.score === "0.0086",
    add_next_message: limitationStep.messages === 1 && limitationStep.status !== "Waiting",
    limitation_example: limitation.messages === 8 && limitation.status === "Below threshold" && limitation.score === "0.0006",
    manual_entry: manual.messages === 1 && manual.status !== "Waiting" && /^0\.\d{4}$/.test(manual.score),
    clear_button: cleared.messages === 0 && cleared.status === "Waiting" && cleared.score === "--",
  };
  const report = { passed: Object.values(checks).every(Boolean), checks, screenshot, snapshots: { initial, flagged, routine, limitationStep, limitation, manual, cleared } };
  console.log(JSON.stringify(report, null, 2));
  if (!report.passed) process.exitCode = 1;
} finally {
  if (cdp?.socket) cdp.socket.close();
  edge.kill();
  await delay(1200);
  if (profile.startsWith(path.join(tmpdir(), "wasd-demo-edge-"))) {
    try {
      await rm(profile, { recursive: true, force: true, maxRetries: 4, retryDelay: 300 });
    } catch (error) {
      console.error(`Temporary Edge profile could not be removed: ${error.message}`);
    }
  }
}
