import { useEffect, useRef, useState } from "react";
import Message from "../../components/Message";
import TypingIndicator from "../../components/TypingIndicator";
import ErrorBanner from "../../components/ErrorBanner";

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const bottomRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage(text) {
    if (!text || !text.trim()) return;

    const token = localStorage.getItem("token");
    if (!token) {
      setError("Session expired. Please login again.");
      return;
    }

    // Add user message immediately
    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: text }),
      });

      if (!response.ok) {
        throw new Error("Failed to reach IntelliDesk service");
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text:
            typeof data.response === "string"
              ? data.response
              : "Sorry, I couldn't understand that.",
        },
      ]);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="chatbot-page">
      <h1>🤖 IntelliDesk Assistant</h1>

      {/* Quick Actions */}
      <div className="quick-actions">
        <button onClick={() => sendMessage("Book a meeting")}>
          📅 Book Meeting
        </button>
        <button onClick={() => sendMessage("I need a laptop")}>
          💻 Request Equipment
        </button>
        <button onClick={() => sendMessage("My system is slow")}>
          🎫 IT Issue
        </button>
      </div>

      {/* Chat Window */}
      <div className="chat-window">
        {messages.length === 0 && (
          <p className="muted">
            Try: <em>“Book a meeting tomorrow at 11”</em>
          </p>
        )}

        {messages.map((msg, index) => (
          <Message key={index} role={msg.role} text={msg.text} />
        ))}

        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {error && <ErrorBanner message={error} />}

      {/* Input Bar */}
      <div className="chat-input">
        <input
          type="text"
          placeholder="Type your message…"
          value={input}
          disabled={loading}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              sendMessage(input);
            }
          }}
        />
        <button onClick={() => sendMessage(input)} disabled={loading}>
          Send
        </button>
      </div>
    </section>
  );
}