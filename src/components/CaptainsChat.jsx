import React, { useEffect, useState } from "react";
import { getChatMessages, postChatMessage } from "../api";

function CaptainsChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getChatMessages()
      .then(setMessages)
      .catch((err) => setError(err.message));
  }, []);

  const sendMessage = async (e) => {
    e.preventDefault();
    try {
      const newMsg = await postChatMessage("Captain", input);
      setMessages((old) => [...old, newMsg]);
      setInput("");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="captains-chat">
      <h2>Captain's Chat</h2>
      {error && <div className="error">Error: {error}</div>}
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className="message">
            <strong>{msg.author}:</strong> {msg.message}
          </div>
        ))}
      </div>
      <form onSubmit={sendMessage}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default CaptainsChat;