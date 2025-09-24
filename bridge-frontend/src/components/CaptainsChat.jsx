import React, { useState, useEffect, useRef } from 'react';
import { getCaptainMessages, sendCaptainMessage } from '../api';

const CaptainsChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchMessages = async () => {
    try {
      setLoading(true);
      const data = await getCaptainMessages();
      setMessages(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch messages:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    try {
      const messageData = {
        message: input.trim(),
        timestamp: new Date().toISOString()
      };
      
      await sendCaptainMessage(messageData);
      setInput('');
      
      // Refresh messages after sending (instant update)
      await fetchMessages();
    } catch (err) {
      setError(err.message);
      console.error('Failed to send message:', err);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  if (loading && messages.length === 0) {
    return (
      <div className="captains-chat">
        <h2>💬 Captains Chat</h2>
        <div className="loading">Loading chat messages...</div>
      </div>
    );
  }

  return (
    <div className="captains-chat">
      <div className="header">
        <h2>💬 Captains Chat</h2>
        <button onClick={fetchMessages} className="refresh-button">🔄 Refresh</button>
      </div>
      
      {error && (
        <div className="error">Error: {error}</div>
      )}
      
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="no-messages">No messages yet</div>
        ) : (
          <div className="messages-list">
            {messages.map((msg, index) => (
              <div key={index} className="message-entry">
                <div className="message-header">
                  <span className="author">{msg.author || 'Captain'}</span>
                  <span className="timestamp">{formatTimestamp(msg.timestamp)}</span>
                </div>
                <div className="message-content">{msg.message}</div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      <form onSubmit={handleSendMessage} className="message-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="message-input"
        />
        <button type="submit" className="send-button">Send</button>
      </form>
    </div>
  );
};

export default CaptainsChat;