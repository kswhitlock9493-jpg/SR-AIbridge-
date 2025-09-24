import React, { useState, useEffect, useRef } from 'react';
import { sendCaptainMessage } from '../api';
import { useBridge } from '../hooks/useBridge';

const CaptainsChat = () => {
  const { 
    captainMessages: messages, 
    realTimeData, 
    loading, 
    error, 
    refreshData 
  } = useBridge();
  
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  /**
   * Handle real-time message updates and scroll to bottom
   */
  useEffect(() => {
    const realTimeMessages = realTimeData.chatMessages || [];
    if (realTimeMessages.length > 0) {
      console.log('📡 Real-time chat messages available:', realTimeMessages.length);
    }
    scrollToBottom();
  }, [messages, realTimeData.chatMessages]);

  /**
   * Handle message sending with optimized refresh
   * Immediately refreshes messages after sending for instant feedback
   */
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    try {
      const messageData = {
        from_: "Bridge Command",
        to: "Fleet",
        message: input.trim(),
        timestamp: new Date().toISOString()
      };
      
      await sendCaptainMessage(messageData);
      setInput('');
      
      // Refresh messages immediately after sending for instant update
      await refreshData('messages');
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
        <button onClick={() => refreshData('messages')} className="refresh-button">🔄 Refresh</button>
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