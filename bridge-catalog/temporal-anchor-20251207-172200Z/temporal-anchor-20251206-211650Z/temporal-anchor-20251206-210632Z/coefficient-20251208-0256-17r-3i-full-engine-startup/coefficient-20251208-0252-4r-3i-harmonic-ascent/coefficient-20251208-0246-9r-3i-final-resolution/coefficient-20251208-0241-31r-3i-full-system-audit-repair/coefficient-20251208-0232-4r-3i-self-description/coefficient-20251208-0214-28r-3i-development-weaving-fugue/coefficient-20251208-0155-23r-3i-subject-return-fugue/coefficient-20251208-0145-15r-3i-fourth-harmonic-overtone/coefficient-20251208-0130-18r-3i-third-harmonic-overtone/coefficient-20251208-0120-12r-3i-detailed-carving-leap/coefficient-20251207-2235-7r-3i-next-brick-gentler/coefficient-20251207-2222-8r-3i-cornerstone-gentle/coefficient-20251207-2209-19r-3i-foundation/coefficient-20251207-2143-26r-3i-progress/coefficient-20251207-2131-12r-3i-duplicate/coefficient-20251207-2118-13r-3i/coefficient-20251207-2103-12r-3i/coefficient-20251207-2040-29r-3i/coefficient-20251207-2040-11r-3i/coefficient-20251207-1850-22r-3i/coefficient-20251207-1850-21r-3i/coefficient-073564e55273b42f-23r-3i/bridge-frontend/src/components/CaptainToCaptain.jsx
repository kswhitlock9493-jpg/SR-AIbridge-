import { useState, useEffect } from 'react';
import { getCaptainMessages, sendCaptainMessage } from '../api';

const CaptainToCaptain = () => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [selectedRecipient, setSelectedRecipient] = useState('all');
  const [messageType, setMessageType] = useState('standard');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentCaptain, setCurrentCaptain] = useState('Captain Alpha');
  const [priority, setPriority] = useState('normal');
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Predefined captain list
  const captains = [
    'Captain Alpha',
    'Captain Beta',
    'Captain Gamma',
    'Captain Delta',
    'Captain Epsilon',
    'Admiral Prime'
  ];

  // Message types
  const messageTypes = {
    standard: { icon: '💬', label: 'Standard' },
    tactical: { icon: '⚔️', label: 'Tactical' },
    intelligence: { icon: '🔍', label: 'Intelligence' },
    logistics: { icon: '📦', label: 'Logistics' },
    medical: { icon: '🏥', label: 'Medical' },
    engineering: { icon: '🔧', label: 'Engineering' },
    diplomatic: { icon: '🤝', label: 'Diplomatic' }
  };

  // Fetch captain messages from backend
  const fetchCaptainMessages = async () => {
    try {
      setError(null);
      const data = await getCaptainMessages();
      setMessages(Array.isArray(data) ? data : []);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Failed to fetch captain messages:', err);
      setError('Failed to load messages: ' + err.message);
    }
  };

  // Send captain-to-captain message
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      setLoading(true);
      setError(null);

      const messageData = {
        author: currentCaptain,
        recipient: selectedRecipient,
        message: newMessage.trim(),
        type: messageType,
        priority: priority,
        timestamp: new Date().toISOString()
      };

      await sendCaptainMessage(messageData);

      setNewMessage('');
      await fetchCaptainMessages(); // Refresh messages
    } catch (err) {
      console.error('Failed to send captain message:', err);
      setError('Failed to send message: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Filter messages based on current captain
  const getFilteredMessages = () => {
    return messages.filter(msg => 
      msg.author === currentCaptain || 
      msg.recipient === currentCaptain || 
      msg.recipient === 'all' ||
      msg.author === 'Admiral Prime' // Admiral messages visible to all
    ).sort((a, b) => {
      const dateA = new Date(a.timestamp || Date.now());
      const dateB = new Date(b.timestamp || Date.now());
      return dateB - dateA; // Most recent first
    });
  };

  // Get priority color
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent':
        return '#dc3545';
      case 'high':
        return '#fd7e14';
      case 'normal':
        return '#28a745';
      case 'low':
        return '#6c757d';
      default:
        return '#007bff';
    }
  };

  // Get message type color
  const getMessageTypeColor = (type) => {
    switch (type) {
      case 'tactical':
        return '#dc3545';
      case 'intelligence':
        return '#6f42c1';
      case 'medical':
        return '#fd7e14';
      case 'engineering':
        return '#20c997';
      case 'diplomatic':
        return '#007bff';
      case 'logistics':
        return '#ffc107';
      default:
        return '#28a745';
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
  };

  // Initial load and periodic refresh
  useEffect(() => {
    fetchCaptainMessages();
    const interval = setInterval(fetchCaptainMessages, 20000); // Refresh every 20 seconds
    return () => clearInterval(interval);
  }, []);

  const filteredMessages = getFilteredMessages();

  return (
    <div className="captain-to-captain">
      <div className="captain-header">
        <h2>⚔️ Captain-to-Captain Communications</h2>
        <div className="header-actions">
          <span className="last-update">
            Last Updated: {lastUpdate.toLocaleTimeString()}
          </span>
          <button onClick={fetchCaptainMessages} className="refresh-btn">
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

      {/* Captain Selection */}
      <div className="captain-selector">
        <label>Active Captain:</label>
        <select 
          value={currentCaptain}
          onChange={(e) => setCurrentCaptain(e.target.value)}
        >
          {captains.map(captain => (
            <option key={captain} value={captain}>{captain}</option>
          ))}
        </select>
      </div>

      <div className="captain-content">
        {/* Message Composer */}
        <div className="message-composer">
          <h3>📝 Compose Message</h3>
          <form onSubmit={handleSendMessage} className="composer-form">
            <div className="composer-header">
              <div className="form-group">
                <label>To:</label>
                <select
                  value={selectedRecipient}
                  onChange={(e) => setSelectedRecipient(e.target.value)}
                >
                  <option value="all">All Captains</option>
                  {captains
                    .filter(captain => captain !== currentCaptain)
                    .map(captain => (
                      <option key={captain} value={captain}>{captain}</option>
                    ))}
                </select>
              </div>

              <div className="form-group">
                <label>Type:</label>
                <select
                  value={messageType}
                  onChange={(e) => setMessageType(e.target.value)}
                >
                  {Object.entries(messageTypes).map(([key, type]) => (
                    <option key={key} value={key}>
                      {type.icon} {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Priority:</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                >
                  <option value="low">Low</option>
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>

            <div className="message-input">
              <textarea
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Enter your message to fellow captains..."
                rows="4"
                maxLength={1000}
                disabled={loading}
              />
              <div className="input-footer">
                <span className="character-count">
                  {newMessage.length}/1000
                </span>
                <button
                  type="submit"
                  disabled={loading || !newMessage.trim()}
                  className="send-btn"
                >
                  {loading ? '⏳ Sending...' : '📤 Send Message'}
                </button>
              </div>
            </div>
          </form>

          {/* Quick Message Templates */}
          <div className="quick-templates">
            <h4>🚀 Quick Templates</h4>
            <div className="template-buttons">
              <button
                onClick={() => setNewMessage('📊 Status report requested. Please provide current fleet status and readiness level.')}
                className="template-btn"
              >
                Status Request
              </button>
              <button
                onClick={() => setNewMessage('🤝 Requesting tactical coordination for joint operation. Please confirm availability.')}
                className="template-btn"
              >
                Coordination Request
              </button>
              <button
                onClick={() => setNewMessage('🚨 Priority alert: Potential threat detected. All captains standby for orders.')}
                className="template-btn"
              >
                Alert Notice
              </button>
              <button
                onClick={() => setNewMessage('📋 Mission briefing scheduled for next watch. All captains required to attend.')}
                className="template-btn"
              >
                Meeting Notice
              </button>
            </div>
          </div>
        </div>

        {/* Messages List */}
        <div className="messages-section">
          <h3>📬 Captain Communications</h3>
          
          {/* Message Statistics */}
          <div className="message-stats">
            <div className="stat-item">
              <span>Total Messages:</span>
              <span>{messages.length}</span>
            </div>
            <div className="stat-item">
              <span>Your Messages:</span>
              <span>{messages.filter(m => m.author === currentCaptain).length}</span>
            </div>
            <div className="stat-item">
              <span>Unread:</span>
              <span>{filteredMessages.filter(m => m.author !== currentCaptain).length}</span>
            </div>
          </div>

          <div className="messages-list">
            {filteredMessages.length > 0 ? (
              filteredMessages.map((message, index) => {
                const { date, time } = formatTimestamp(message.timestamp || Date.now());
                const isOwnMessage = message.author === currentCaptain;
                const messageTypeInfo = messageTypes[message.type] || messageTypes.standard;

                return (
                  <div
                    key={message.id || index}
                    className={`captain-message ${isOwnMessage ? 'own-message' : 'received-message'}`}
                  >
                    <div className="message-header">
                      <div className="message-info">
                        <span className="author">{message.author}</span>
                        <span className="recipient">→ {message.recipient || 'All'}</span>
                        <span className="timestamp">{date} {time}</span>
                      </div>
                      <div className="message-badges">
                        <span
                          className="type-badge"
                          style={{ backgroundColor: getMessageTypeColor(message.type) }}
                        >
                          {messageTypeInfo.icon} {messageTypeInfo.label}
                        </span>
                        <span
                          className="priority-badge"
                          style={{ backgroundColor: getPriorityColor(message.priority) }}
                        >
                          {message.priority || 'normal'}
                        </span>
                      </div>
                    </div>
                    <div className="message-content">
                      {message.message || message.content || 'No message content'}
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="no-messages">
                <span>⚔️</span>
                <p>No captain communications yet.</p>
                <p>Start coordinating with fellow captains!</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Communication Guidelines */}
      <div className="communication-guidelines">
        <h4>📋 Communication Protocol</h4>
        <div className="guidelines-list">
          <div className="guideline">
            <span className="guideline-icon">🔒</span>
            <span>All communications are logged and monitored</span>
          </div>
          <div className="guideline">
            <span className="guideline-icon">⚡</span>
            <span>Use appropriate priority levels for urgent matters</span>
          </div>
          <div className="guideline">
            <span className="guideline-icon">🎯</span>
            <span>Select specific message types for better organization</span>
          </div>
          <div className="guideline">
            <span className="guideline-icon">🤝</span>
            <span>Maintain professional military communication standards</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CaptainToCaptain;