document.addEventListener("DOMContentLoaded", function () {

  const input = document.getElementById("userInput");
  const sendBtn = document.getElementById("sendBtn");
  const chatArea = document.getElementById("chatArea");
  const typingIndicator = document.getElementById("typingIndicator");
  const toggle = document.getElementById("modeToggle");

  let currentMode = "normal";

  // 🔥 Clear any hardcoded messages on load
  chatArea.innerHTML = "";

  // 🕒 Get Current Time
  function getTime() {
    const now = new Date();
    return now.toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  // 💬 Add Message
  function addMessage(text, type) {

    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", type);

    const bubble = document.createElement("div");
    bubble.classList.add("bubble");

    bubble.innerHTML = `
      ${text}
      <div class="meta">${getTime()}</div>
    `;

    messageDiv.appendChild(bubble);
    chatArea.appendChild(messageDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  // 🔁 Mode Toggle
  if (toggle) {
    toggle.addEventListener("change", function () {
      currentMode = this.checked ? "krishna" : "normal";
    });
  }

  // 🚀 Send Message
  async function sendMessage() {

    const message = input.value.trim();
    if (!message) return;

    addMessage(message, "user-message");
    input.value = "";
    typingIndicator.classList.remove("hidden");

    try {

      const res = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message: message,
          mode: currentMode
        })
      });

      const data = await res.json();
      typingIndicator.classList.add("hidden");

      if (currentMode === "krishna") {

        const formatted = `
          <b>📖 Gita ${data.chapter}:${data.verse}</b><br><br>
          🕉 ${data.text}<br><br>
          <b>Meaning:</b><br>${data.meaning}
        `;

        addMessage(formatted, "ai-message");

      } else {
        addMessage(data.reply, "ai-message");
      }

    } catch (error) {
      typingIndicator.classList.add("hidden");
      addMessage("⚠ Backend error. Please check server.", "ai-message");
      console.error(error);
    }
  }

  sendBtn.addEventListener("click", sendMessage);

  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      sendMessage();
    }
  });

});