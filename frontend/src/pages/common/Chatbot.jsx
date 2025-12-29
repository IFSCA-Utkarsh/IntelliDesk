import { useState } from "react";
import Spinner from "../../components/Spinner";
import ErrorBanner from "../../components/ErrorBanner";

export default function Chatbot() {
  const user = JSON.parse(localStorage.getItem("user"));
  const role = user?.role;

  const [message, setMessage] = useState("");
  const [responses, setResponses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function sendMessage(customMessage) {
    const finalMessage = customMessage ?? message;
    if (!finalMessage.trim()) return;

    const token = localStorage.getItem("token");
    if (!token) {
      setError("Session expired. Please login again.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          message: finalMessage,
          role // optional, backend may ignore safely
        })
      });

      if (!res.ok) {
        throw new Error("Chat service unavailable");
      }

      const data = await res.json();

      setResponses(prev => [
        ...prev,
        { role: "user", text: finalMessage },
        { role: "bot", data }
      ]);

      setMessage("");
    } catch (err) {
      setError(err.message || "Failed to send message");
    } finally {
      setLoading(false);
    }
  }

  function renderBotResponse(data) {
    if (!data) return null;

    switch (data.route) {
      case "reply":
        return <p>{data.response}</p>;

      case "meeting":
        return (
          <div className="bot-card">
            <strong>Meeting Request Detected</strong>
            <pre>{JSON.stringify(data.extracted_details, null, 2)}</pre>
          </div>
        );

      case "ticket":
        return (
          <div className="bot-card">
            <strong>Suggested IT Ticket</strong>
            <p>{data.suggested_issue}</p>
          </div>
        );

      default:
        return <pre>{JSON.stringify(data, null, 2)}</pre>;
    }
  }

  return (
    <section className="chatbot-page">
      <h1>Chatbot</h1>

      {/* 🔹 QUICK ACTIONS */}
      <div className="quick-actions">
        <button onClick={() => sendMessage("I want to book a meeting")}>
          Book Meeting
        </button>

        <button onClick={() => sendMessage("I have an IT issue")}>
          Raise IT Ticket
        </button>

        {role !== "user" && (
          <button onClick={() => sendMessage("Show all system issues")}>
            View System Issues
          </button>
        )}
      </div>

      <div className="chat-window">
        {responses.length === 0 && (
          <p className="muted">
            Ask something like “Schedule a meeting tomorrow”
          </p>
        )}

        {responses.map((item, index) => (
          <div
            key={index}
            className={`chat-message ${item.role} fade-in`}
          >
            {item.role === "user" ? (
              <div className="user-msg">{item.text}</div>
            ) : (
              <div className="bot-msg">
                {renderBotResponse(item.data)}
              </div>
            )}
          </div>
        ))}

        {loading && <Spinner />}
      </div>

      {error && <ErrorBanner message={error} />}

      <div className="chat-input">
        <input
          placeholder="Type your message…"
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={e => e.key === "Enter" && sendMessage()}
          disabled={loading}
        />
        <button onClick={() => sendMessage()} disabled={loading}>
          Send
        </button>
      </div>
    </section>
  );
}
