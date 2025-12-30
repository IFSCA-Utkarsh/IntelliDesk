export default function Message({ role, text }) {
  const isUser = role === "user";

  return (
    <div className={`chat-message ${isUser ? "user" : "bot"} fade-in`}>
      {isUser ? (
        <div className="user-msg">{text}</div>
      ) : (
        <div className="bot-msg">{text}</div>
      )}
    </div>
  );
}
