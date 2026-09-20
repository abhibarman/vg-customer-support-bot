const appEl = document.querySelector(".app");
const threadEl = document.getElementById("thread");
const welcomeEl = document.getElementById("welcome");
const gateEl = document.getElementById("gate");
const gateCopyEl = document.getElementById("gate-copy");
const signInEl = document.getElementById("sign-in");
const signOutEl = document.getElementById("sign-out");
const userLabelEl = document.getElementById("user-label");
const dockEl = document.querySelector(".dock");
const stageEl = document.getElementById("stage");
const formEl = document.getElementById("composer");
const inputEl = document.getElementById("message");
const sendEl = document.getElementById("send");
const newChatEl = document.getElementById("new-chat");
const statusEl = document.getElementById("status");
const statusLabel = document.getElementById("status-label");

const history = [];
let busy = false;

if (window.marked) {
  marked.setOptions({ gfm: true, breaks: true });
}

function renderMarkdown(text) {
  const raw = String(text || "");
  if (window.marked && window.DOMPurify) {
    return DOMPurify.sanitize(marked.parse(raw));
  }
  const escaped = raw
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
  return escaped.replaceAll("\n", "<br>");
}

function resizeComposer() {
  inputEl.style.height = "auto";
  inputEl.style.height = `${Math.min(inputEl.scrollHeight, 160)}px`;
  sendEl.disabled = busy || !inputEl.value.trim();
}

function scrollToEnd() {
  stageEl.scrollTop = stageEl.scrollHeight;
}

function setStatus(state, label) {
  statusEl.dataset.state = state;
  statusLabel.textContent = label;
}

function showConversation() {
  welcomeEl.hidden = true;
  threadEl.hidden = false;
  newChatEl.hidden = false;
}

function pruneFailedAssistant() {
  const last = threadEl.lastElementChild;
  if (last?.classList.contains("assistant") && last.querySelector(".error")) {
    last.remove();
  }
}

function lastUserText() {
  const lastUser = [...threadEl.querySelectorAll(".turn.user")].at(-1);
  return lastUser?.querySelector(".bubble")?.textContent || "";
}

function resetConversation() {
  history.length = 0;
  busy = false;
  threadEl.replaceChildren();
  threadEl.hidden = true;
  welcomeEl.hidden = false;
  newChatEl.hidden = true;
  inputEl.value = "";
  resizeComposer();
  inputEl.focus();
}

function addUserTurn(text) {
  const item = document.createElement("li");
  item.className = "turn user";
  item.innerHTML = `<div class="bubble"></div>`;
  item.querySelector(".bubble").textContent = text;
  threadEl.append(item);
}

function addAssistantTurn() {
  const item = document.createElement("li");
  item.className = "turn assistant";
  item.innerHTML = `
    <div class="avatar" aria-hidden="true">V</div>
    <div class="bubble">
      <div class="bubble-meta">
        <span class="who">Support assistant</span>
        <button class="copy" type="button" hidden>Copy</button>
      </div>
      <div class="markdown"></div>
    </div>
  `;
  threadEl.append(item);
  return item;
}

function setTyping(item) {
  const body = item.querySelector(".markdown");
  body.innerHTML = `<div class="typing" aria-label="Assistant is typing"><span></span><span></span><span></span></div>`;
}

function setReply(item, text) {
  const body = item.querySelector(".markdown");
  const copyBtn = item.querySelector(".copy");
  body.innerHTML = renderMarkdown(text);
  copyBtn.hidden = false;
  copyBtn.addEventListener("click", async () => {
    await navigator.clipboard.writeText(text);
    copyBtn.textContent = "Copied";
    setTimeout(() => {
      copyBtn.textContent = "Copy";
    }, 1400);
  });
}

function setError(item, message, retryText) {
  item.querySelector(".bubble").classList.add("error");
  const body = item.querySelector(".markdown");
  body.replaceChildren();
  const p = document.createElement("p");
  p.textContent = message;
  const retry = document.createElement("button");
  retry.className = "retry";
  retry.type = "button";
  retry.textContent = "Try again";
  retry.addEventListener("click", () => sendMessage(retryText));
  body.append(p, retry);
}

function errorDetail(detail) {
  if (typeof detail === "string" && detail) return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
  return "The support model could not complete that request.";
}

async function sendMessage(text) {
  const message = text.trim();
  if (!message || busy) return;

  busy = true;
  showConversation();
  const retryingFailed = Boolean(threadEl.lastElementChild?.querySelector(".error")) && lastUserText() === message;
  pruneFailedAssistant();
  if (!retryingFailed) addUserTurn(message);
  const assistantItem = addAssistantTurn();
  setTyping(assistantItem);
  inputEl.value = "";
  resizeComposer();
  scrollToEnd();

  try {
    const response = await fetch("/chat", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history }),
    });
    if (response.status === 401) {
      window.location.href = "/auth/login";
      return;
    }
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(errorDetail(payload.detail));
    }
    const reply = payload.reply || "";
    history.push({ role: "user", content: message }, { role: "assistant", content: reply });
    setReply(assistantItem, reply);
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Something went wrong.";
    setError(assistantItem, detail, message);
  } finally {
    busy = false;
    resizeComposer();
    scrollToEnd();
    inputEl.focus();
  }
}

async function checkHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("down");
    setStatus("ok", "Online");
  } catch {
    setStatus("down", "Unavailable");
  }
}

formEl.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage(inputEl.value);
});

inputEl.addEventListener("input", resizeComposer);
inputEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage(inputEl.value);
  }
});

document.getElementById("prompts").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-prompt]");
  if (button) sendMessage(button.dataset.prompt);
});

function showSignedOut(configured) {
  appEl.classList.add("signed-out");
  gateEl.hidden = false;
  welcomeEl.hidden = true;
  threadEl.hidden = true;
  dockEl.hidden = true;
  statusEl.hidden = true;
  newChatEl.hidden = true;
  signOutEl.hidden = true;
  userLabelEl.hidden = true;
  if (configured) {
    gateCopyEl.textContent = "Sign in with Auth0 to open Vanguard Support.";
    signInEl.removeAttribute("aria-disabled");
    signInEl.href = "/auth/login";
  } else {
    gateCopyEl.textContent =
      "Auth0 is not configured yet. Create a Regular Web Application, then set AUTH0_DOMAIN, OIDC_CLIENT_ID, and OIDC_CLIENT_SECRET in .env.";
    signInEl.setAttribute("aria-disabled", "true");
    signInEl.removeAttribute("href");
  }
}

function showSignedIn(user) {
  appEl.classList.remove("signed-out");
  gateEl.hidden = true;
  welcomeEl.hidden = false;
  dockEl.hidden = false;
  statusEl.hidden = false;
  signOutEl.hidden = false;
  userLabelEl.hidden = false;
  userLabelEl.textContent = user.email || user.name || "Signed in";
  userLabelEl.title = user.email || "";
  resizeComposer();
  inputEl.focus();
}

async function loadSession() {
  const session = await OidcAuth.getSession();
  if (session.authenticated) {
    showSignedIn(session);
    checkHealth();
    setInterval(checkHealth, 30000);
    return;
  }
  showSignedOut(Boolean(session.configured));
}

newChatEl.addEventListener("click", resetConversation);

resizeComposer();
loadSession();
