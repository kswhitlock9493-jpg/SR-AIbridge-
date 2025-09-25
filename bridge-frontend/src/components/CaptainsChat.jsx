import React, { useState, useEffect, useRef } from 'react';
import { getCaptainMessages, sendCaptainMessage } from '../api';

const CaptainsChat = () => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentUser, setCurrentUser] = useState('Admiral');
  const [isConnected, setIsConnected] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const messagesEndRef = useRef(null);

  // Fetch messages from backend
  const fetchMessages = async () => {
    try {
      setError(null);
      const data = await getCaptainMessages();
      setMessages(Array.isArray(data) ? data : []);
      setLastUpdate(new Date());
      setIsConnected(true);
    } catch (err) {
      console.error('Failed to fetch captain messages:', err);
      setError('Failed to load messages: ' + err.message);
      setIsConnected(false);
    }
  };

  // Send new message
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      setLoading(true);
      setError(null);

      await sendCaptainMessage({
        author: currentUser,
        message: newMessage.trim(),
        timestamp: new Date().toISOString()
      });

      setNewMessage('');
      await fetchMessages(); // Refresh messages
      setIsConnected(true);
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message: ' + err.message);
      setIsConnected(false);
    } finally {
      setLoading(false);
    }
  };

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Get message time difference for grouping
  const shouldShowTimestamp = (currentMsg, previousMsg) => {
    if (!previousMsg) return true;
    
    const currentTime = new Date(currentMsg.timestamp || Date.now());
    const previousTime = new Date(previousMsg.timestamp || Date.now());
    const timeDiff = currentTime - previousTime;
    
    return timeDiff > 300000; // Show timestamp if more than 5 minutes apart
  };

  // Get user avatar/icon
  const getUserIcon = (author) => {
    const icons = {
      'Admiral': '⚓',
      'Captain': '👨‍✈️',
      'Commander': '🎖️',
      'Lieutenant': '🎭',
      'Ensign': '🔰',
      'AI': '🤖'
    };
    return icons[author] || '👤';
  };

  // Get user color
  const getUserColor = (author) => {
    const colors = {
      'Admiral': '#dc3545',
      'Captain': '#007bff',
      'Commander': '#28a745',
      'Lieutenant': '#ffc107',
      'Ensign': '#6f42c1',
      'AI': '#20c997'
    };
    return colors[author] || '#6c757d';
  };

  // Initial load and periodic refresh
  useEffect(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, 15000); // Refresh every 15 seconds
    return () => clearInterval(interval);
  }, []);

  // Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="captains-chat">
      <div className="chat-header">
        <div className="header-title">
          <h2>💬 Captains Communications</h2>
          <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
            <span className="status-indicator">●</span>
            <span className="status-text">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
        <div className="header-actions">
          <span className="last-update">
            Last Updated: {lastUpdate.toLocaleTimeString()}
          </span>
          <button onClick={fetchMessages} className="refresh-btn">
            🔄 Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️</span>
          <span>{error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* User Selection */}
      <div className="user-selector">
        <label>Speaking as:</label>
        <select
          value={currentUser}
          onChange={(e) => setCurrentUser(e.target.value)}
        >
          <option value="Admiral">Admiral</option>
          <option value="Captain">Captain</option>
          <option value="Commander">Commander</option>
          <option value="Lieutenant">Lieutenant</option>
          <option value="Ensign">Ensign</option>
        </select>
      </div>

      {/* Messages Container */}
      <div className="messages-container">
        {messages.length > 0 ? (
          <>
            {messages.map((message, index) => {
              const previousMessage = index > 0 ? messages[index - 1] : null;
              const showTimestamp = shouldShowTimestamp(message, previousMessage);
              const isOwnMessage = message.author === currentUser;

              return (
                <div key={message.id || index}>
                  {showTimestamp && (
                    <div className="timestamp-divider">
                      <span>{formatTimestamp(message.timestamp || Date.now())}</span>
                    </div>
                  )}
                  <div className={`message ${isOwnMessage ? 'own-message' : 'other-message'}`}>
                    <div className="message-avatar">
                      <span
                        className="avatar-icon"
                        style={{ color: getUserColor(message.author) }}
                      >
                        {getUserIcon(message.author)}
                      </span>
                    </div>
                    <div className="message-content">
                      <div className="message-header">
                        <span
                          className="author-name"
                          style={{ color: getUserColor(message.author) }}
                        >
                          {message.author || 'Unknown'}
                        </span>
                        <span className="message-time">
                          {formatTimestamp(message.timestamp || Date.now())}
                        </span>
                      </div>
                      <div className="message-text">
                        {message.message || message.content || 'No message content'}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </>
        ) : (
          <div className="no-messages">
            <span>💬</span>
            <p>No messages yet. Start the conversation!</p>
          </div>
        )}
      </div>

      {/* Message Input */}
      <form onSubmit={handleSendMessage} className="message-input-container">
        <div className="input-wrapper">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type your message..."
            disabled={loading}
            maxLength={500}
          />
          <div className="input-actions">
            <span className="character-count">
              {newMessage.length}/500
            </span>
            <button
              type="submit"
              disabled={loading || !newMessage.trim()}
              className="send-btn"
            >
              {loading ? '⏳' : '📤'} Send
            </button>
          </div>
        </div>
      </form>

      {/* Chat Statistics */}
      <div className="chat-stats">
        <div className="stat-item">
          <span>Total Messages:</span>
          <span>{messages.length}</span>
        </div>
        <div className="stat-item">
          <span>Active Participants:</span>
          <span>{new Set(messages.map(m => m.author)).size}</span>
        </div>
        <div className="stat-item">
          <span>Last Activity:</span>
          <span>
            {messages.length > 0
              ? formatTimestamp(messages[messages.length - 1].timestamp || Date.now())
              : 'None'
            }
          </span>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <button
          onClick={() => {
            const status = `🛰️ System Status: All stations operational. ${new Date().toLocaleTimeString()}`;
            setNewMessage(status);
          }}
          className="quick-action-btn"
        >
          📊 Status Update
        </button>
        <button
          onClick={() => {
            const alert = `🚨 Alert: All hands to battle stations! This is not a drill.`;
            setNewMessage(alert);
          }}
          className="quick-action-btn"
        >
          🚨 Battle Alert
        </button>
        <button
          onClick={() => {
            const sitrep = `📋 SITREP: Awaiting orders. Fleet ready for deployment.`;
            setNewMessage(sitrep);
          }}
          className="quick-action-btn"
        >
          📋 SITREP
        </button>
      </div>
    </div>
  );
};

export default CaptainsChat;