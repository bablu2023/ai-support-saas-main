(function () {
  const script = document.currentScript;
  const ORG_API_KEY = script.getAttribute("data-org-key");
  console.log("WIDGET ORG API KEY =", ORG_API_KEY);


  if (!ORG_API_KEY) {
    console.error("AI Widget: data-org-key is missing");
    return;
  }

  /* ---------- Inject CSS ---------- */
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = script.src.replace("widget.js", "widget.css");
  document.head.appendChild(link);

  /* ---------- Floating Button ---------- */
  const btn = document.createElement("div");
  btn.id = "ai-widget-button";
  btn.innerText = "💬";
  document.body.appendChild(btn);

  /* ---------- Chat Box ---------- */
  const chat = document.createElement("div");
  chat.id = "ai-widget-chat";
  chat.innerHTML = `
    <div id="ai-widget-header">AI Support</div>
    <div id="ai-widget-messages"></div>
    <div id="ai-widget-input">
      <input type="text" placeholder="Ask a question..." />
      <button>Send</button>
    </div>
  `;
  document.body.appendChild(chat);

  btn.onclick = () => {
    chat.style.display = chat.style.display === "flex" ? "none" : "flex";
  };

  const input = chat.querySelector("input");
  const sendBtn = chat.querySelector("button");
  const messages = chat.querySelector("#ai-widget-messages");

  function addMessage(text, isUser) {
    const div = document.createElement("div");
    div.style.margin = "8px 0";
    div.style.textAlign = isUser ? "right" : "left";
    div.innerText = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function addTyping() {
    const div = document.createElement("div");
    div.id = "typing";
    div.innerText = "Typing...";
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function removeTyping() {
    const t = document.getElementById("typing");
    if (t) t.remove();
  }

  /* ---------- Send Message ---------- */
  sendBtn.onclick = async () => {
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, true);
    input.value = "";
    addTyping();

    try {
      const res = await fetch("/api/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          api_key: ORG_API_KEY,
          user_id: "web_widget",
          question: text
        })
      });

      removeTyping();

      if (!res.ok) {
        addMessage("Server error (" + res.status + ")", false);
        return;
      }

      const data = await res.json();

      if (data.answer) {
        addMessage(data.answer, false);
      } else if (data.error) {
        addMessage("Error: " + data.error, false);
      } else {
        addMessage("Unexpected server response.", false);
      }

    } catch (err) {
      removeTyping();
      addMessage("Unable to reach server.", false);
      console.error("Widget error:", err);
    }
  };
})();
