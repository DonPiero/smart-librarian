let token = null;
let currentConversationId = null;

function showLogin() {
  document.getElementById("login-form").classList.remove("hidden");
  document.getElementById("register-form").classList.add("hidden");
  document.getElementById('login-toggle').classList.add('selected');
  document.getElementById('register-toggle').classList.remove('selected');
}

function showRegister() {
  document.getElementById("register-form").classList.remove("hidden");
  document.getElementById("login-form").classList.add("hidden");
  document.getElementById('login-toggle').classList.remove('selected');
  document.getElementById('register-toggle').classList.add('selected');
}

document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("register-username").value;
  const password = document.getElementById("register-password").value;

  const res = await fetch("/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();

  if (res.ok) {
    const loginRes = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const loginData = await loginRes.json();

    if (loginRes.ok) {
        token = loginData.access_token;
        localStorage.setItem("token", token);

        document.querySelector(".auth-box").classList.add("hidden");
        document.querySelector(".main-page").classList.remove("hidden");
        document.getElementById("login-status").innerText = "";
        loadConversations();
    } else {
        document.getElementById("register-status").innerText = "Account successfully created, but authentication failed.";
    }
  } else {
    document.getElementById("register-status").innerText = data.detail;
  }
});

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;

  const res = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();

  if (res.ok) {
    token = data.access_token;
    localStorage.setItem("token", token);
    document.getElementById("login-status").innerText = "Authenticated successfully!";

    document.querySelector(".auth-box").classList.add("hidden");
    document.querySelector(".main-page").classList.remove("hidden");
    document.getElementById("login-status").innerText = "";
    loadConversations();
  } else {
    document.getElementById("login-status").innerText = data.detail;
  }
});

document.getElementById("logout-button").addEventListener("click", () => {
  localStorage.removeItem("token");
  token = null;
  currentConversationId = null;
  document.getElementById("messages").innerHTML = "";
  document.querySelector(".main-page").classList.add("hidden");
  document.querySelector(".auth-box").classList.remove("hidden");
  showLogin();
});

async function apiFetch(url, options = {}) {
  options.headers = options.headers || {};
  options.headers["Authorization"] = "Bearer " + localStorage.getItem("token");
  return fetch(url, options);
}

function renderMessage(role, content, isMedia = false) {
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", role);

  if (isMedia) {
    msgDiv.appendChild(content);
  } else {
    msgDiv.textContent = content;
  }

  document.getElementById("messages").appendChild(msgDiv);
  msgDiv.scrollIntoView();
}

function addDownloadLink(containerEl, blob, filename) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.textContent = "Download";
  link.classList.add("download-link");
  containerEl.appendChild(document.createElement("br"));
  containerEl.appendChild(link);
}

async function loadConversations() {
  const res = await apiFetch("/conversations");
  if (!res.ok) return;
  const convos = await res.json();
  const list = document.getElementById("chat-list");
  list.innerHTML = "";

  convos.forEach(c => {
    const li = document.createElement("li");
    li.textContent = c.title;
    li.classList.add("chat-item");
    li.onclick = () => openConversation(c.id);

    const delBtn = document.createElement("button");
    delBtn.textContent = "🗑";
    delBtn.classList.add("delete-chat");
    delBtn.onclick = async (e) => {
      e.stopPropagation();
      await apiFetch(`/conversations/${c.id}`, { method: "DELETE" });
      loadConversations();
      if (currentConversationId === c.id) {
        currentConversationId = null;
        document.getElementById("messages").innerHTML = "";
      }
    };

    li.appendChild(delBtn);
    list.appendChild(li);
  });
}

async function openConversation(id) {
  const res = await apiFetch(`/conversations/${id}`);
  if (!res.ok) return;
  const data = await res.json();

  currentConversationId = data.conversation.id;
  document.getElementById("messages").innerHTML = "";
  data.messages.forEach(m => renderMessage(m.role, m.content));
}

document.getElementById("new-chat").addEventListener("click", () => {
  currentConversationId = null;
  document.getElementById("messages").innerHTML = "";
});

document.getElementById("send-btn").addEventListener("click", async () => {
  const input = document.getElementById("message-input");
  const text = input.value.trim();
  if (!text) return;
  renderMessage("user", text);
  input.value = "";

  if (!currentConversationId) {
    const convRes = await apiFetch("/conversations", { method: "POST" });
    const conv = await convRes.json();
    currentConversationId = conv.id;
    loadConversations();
  }

  const res = await apiFetch(`/conversations/${currentConversationId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: text })
  });

  if (res.ok) {
    const data = await res.json();
    const lastMsg = data.messages[data.messages.length - 1];
    renderMessage("assistant", lastMsg.content);
  }
});

let mediaRecorder;
let audioChunks = [];
let recording = false;

document.getElementById("stt-btn").addEventListener("click", async () => {
  if (!currentConversationId) {
    alert("Send your first text message to start a chat before using STT.");
    return;
  }

  if (!recording) {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      const form = new FormData();
      form.append("file", audioBlob, "audio.webm");

      const res = await apiFetch(`/conversations/${currentConversationId}/stt`, {
        method: "POST",
        body: form
      });
      if (res.ok) {
        const data = await res.json();
        const lastTwo = data.messages.slice(-2);
        lastTwo.forEach(m => renderMessage(m.role, m.content));
      }
    };

    mediaRecorder.start();
    recording = true;
    document.getElementById("stt-btn").textContent = "Stop Recording";
  } else {
    mediaRecorder.stop();
    recording = false;
    document.getElementById("stt-btn").textContent = "Speech to Text";
  }
});

document.getElementById("tts-btn").addEventListener("click", async () => {
  if (!currentConversationId) return;
  const res = await apiFetch(`/conversations/${currentConversationId}/tts`);
  if (!res.ok) return;

  const blob = await res.blob();
  const audio = document.createElement("audio");
  audio.controls = true;
  audio.src = URL.createObjectURL(blob);

  const wrap = document.createElement("div");
  wrap.appendChild(audio);
  addDownloadLink(wrap, blob, "response.mp3");
  renderMessage("assistant", wrap, true);
});

document.getElementById("img-btn").addEventListener("click", async () => {
  if (!currentConversationId) return;
  const res = await apiFetch(`/conversations/${currentConversationId}/image`);
  if (!res.ok) return;

  const blob = await res.blob();
  const img = document.createElement("img");
  img.src = URL.createObjectURL(blob);
  img.classList.add("chat-image");

  const wrap = document.createElement("div");
  wrap.appendChild(img);
  addDownloadLink(wrap, blob, "image.png");
  renderMessage("assistant", wrap, true);
});