import React, { useState, useEffect, useRef } from 'react';
import { getCaptainMessages, sendCaptainMessage } from '../api';
import { usePolling } from '../hooks/usePolling';

const CaptainsChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  /**
   * Optimized message fetching for chat functionality
   * Handles message state management efficiently
   */
  const fetchMessages = async () => {
    const data = await getCaptainMessages();
    setMessages(data);
    return data;
  };

  /**
   * Use 30-second polling for chat messages
   * While chat might benefit from more frequent updates, 30 seconds provides
   * a good balance between real-time feel and network efficiency.
   * Manual refresh is available for immediate updates when needed.
   */
  const { loading, error, refresh } = usePolling(fetchMessages, {
    interval: 30000, // 30 seconds - balanced for chat monitoring with manual refresh option
    immediate: true,
    debounceDelay: 100 // Shorter debounce for chat for more responsive feel
  });

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  /**
   * Handle message sending with optimized refresh
   * Immediately refreshes messages after sending for instant feedback
   */
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
      
      // Refresh messages immediately after sending for instant update
      await refresh();
    } catch (err) {
      console.error('Failed to send message:', err);
      // Error handling is managed by the polling hook
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
        {/* Manual refresh for immediate message updates */}
        <button onClick={refresh} className="refresh-button">🔄 Refresh</button>
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