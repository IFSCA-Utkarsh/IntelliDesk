import { useEffect, useRef, useState } from "react";
import { sendChat, getChatHistory } from "../api/client";
import Message from "../components/Message";
import TypingIndicator from "../components/TypingIndicator";

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    getChatHistory().then((res) => {
      if (res.history) {
        setMessages(
          res.history.map((m) => ({
            role: m.role,
            text: m.content,
          }))
        );
      }
    });
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send(text) {
    if (!text.trim()) return;

    setMessages((m) => [...m, { role: "user", text }]);
    setInput("");
    setLoading(true);

    const res = await sendChat(text);

    setMessages((m) => [
      ...m,
      {
        role: "assistant",
        text: res.response,
        suggestions: res.suggestions,
      },
    ]);

    setLoading(false);
  }

  return (
    <div className="flex flex-col h-screen bg-zinc-100 dark:bg-zinc-900">
      <header className="p-4 bg-white dark:bg-zinc-800 shadow flex justify-between">
        <h1 className="font-semibold">🤖 IntelliDesk</h1>
        <button
          onClick={() => {
            document.documentElement.classList.toggle("dark");
            localStorage.theme =
              document.documentElement.classList.contains("dark")
                ? "dark"
                : "light";
          }}
        >
          🌙
        </button>
      </header>

      <main className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((m, i) => (
          <Message key={i} {...m} onSlot={send} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </main>

      <footer className="p-4 bg-white dark:bg-zinc-800 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send(input)}
          placeholder="Type your message..."
          className="flex-1 px-4 py-2 rounded-xl border
            dark:bg-zinc-700 dark:text-white"
        />
        <button
          onClick={() => send(input)}
          className="px-5 py-2 rounded-xl bg-blue-600 text-white"
        >
          Send
        </button>
      </footer>
    </div>
  );
}