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
  const [sendError, setSendError] = useState(null);
  const [isSending, setIsSending] = useState(false);
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
   * Enhanced message sending with better error handling and retry capability
   */
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || isSending) return;

    setIsSending(true);
    setSendError(null);

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
      
      // Clear any previous errors on successful send
      setSendError(null);
    } catch (err) {
      console.error('Failed to send message:', err);
      setSendError(err.message || 'Failed to send message. Please try again.');
      
      // Don't clear the input on error so user can retry
    } finally {
      setIsSending(false);
    }
  };

  /**
   * Retry sending the last message
   */
  const retryLastMessage = () => {
    if (input.trim()) {
      handleSendMessage({ preventDefault: () => {} });
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  if (loading && messages.length === 0) {
    return (
      <div className="captains-chat">
        <h2>💬 Captains Chat</h2>
        <div className="loading">
          <div className="loading-spinner"></div>
          Loading chat messages...
        </div>
      </div>
    );
  }

  return (
    <div className="captains-chat">
      <div className="header">
        <h2>💬 Captains Chat</h2>
        <div className="header-controls">
          {/* Manual refresh for immediate message updates */}
          <button 
            onClick={() => refreshData('messages')} 
            className="refresh-button"
            disabled={loading}
            title="Refresh messages"
          >
            {loading ? '⏳' : '🔄'} Refresh
          </button>
          <div className="connection-status">
            <span className={`status-indicator ${realTimeData.chatMessages?.length > 0 ? 'live' : 'polling'}`}>
              {realTimeData.chatMessages?.length > 0 ? '🔴 LIVE' : '📡 POLLING'}
            </span>
          </div>
        </div>
      </div>
      
      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span className="error-message">Connection Error: {error}</span>
          <button onClick={() => refreshData('messages')} className="error-retry">
            🔄 Retry
          </button>
        </div>
      )}
      
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="no-messages">
            <div className="placeholder-icon">💬</div>
            <div className="placeholder-title">No messages yet</div>
            <div className="placeholder-subtitle">Start the conversation with your fleet</div>
          </div>
        ) : (
          <div className="messages-list">
            {messages.map((msg, index) => (
              <div key={index} className="message-entry">
                <div className="message-header">
                  <span className="author">{msg.author || msg.from_ || 'Captain'}</span>
                  <span className="timestamp">{formatTimestamp(msg.timestamp)}</span>
                </div>
                <div className="message-content">{msg.message}</div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      {sendError && (
        <div className="send-error">
          <span className="error-icon">⚠️</span>
          <span className="error-text">{sendError}</span>
          <button onClick={retryLastMessage} className="retry-button" disabled={!input.trim()}>
            🔄 Retry
          </button>
        </div>
      )}
      
      <form onSubmit={handleSendMessage} className="message-form">
        <div className="input-group">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message to the fleet..."
            className="message-input"
            disabled={isSending}
            maxLength={500}
          />
          <button 
            type="submit" 
            className="send-button"
            disabled={!input.trim() || isSending}
            title={!input.trim() ? 'Enter a message to send' : 'Send message'}
          >
            {isSending ? (
              <>
                <span className="spinner"></span>
                Sending...
              </>
            ) : (
              <>
                📤 Send
              </>
            )}
          </button>
        </div>
        <div className="input-footer">
          <span className="char-count">{input.length}/500</span>
          <span className="send-hint">Press Enter to send</span>
        </div>
      </form>
    </div>
  );
};

export default CaptainsChat;