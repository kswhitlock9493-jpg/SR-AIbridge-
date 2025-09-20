class AgentManager {
    constructor(container) {
        this.container = container;
        this.agents = [];
        this.apiBaseUrl = 'http://localhost:8000';
        this.refreshInterval = null;
    }

    async init() {
        this.render();
        await this.loadAgents();
        this.startAutoRefresh();
    }

    render() {
        this.container.innerHTML = `
            <div class="agent-manager">
                <div class="manager-header">
                    <h2>🤖 Agent Fleet Management</h2>
                    <div class="manager-actions">
                        <button id="refresh-btn" class="btn btn-secondary">🔄 Refresh</button>
                        <button id="register-btn" class="btn btn-primary">➕ Register Agent</button>
                    </div>
                </div>
                
                <div class="agent-stats">
                    <div class="stat-card">
                        <div class="stat-number" id="total-agents">0</div>
                        <div class="stat-label">Total Agents</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="online-agents">0</div>
                        <div class="stat-label">Online</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="offline-agents">0</div>
                        <div class="stat-label">Offline</div>
                    </div>
                </div>

                <div class="agent-list" id="agent-list">
                    <div class="loading">Loading agents...</div>
                </div>

                <!-- Registration Modal -->
                <div id="register-modal" class="modal" style="display: none;">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3>Register New Agent</h3>
                            <button id="close-modal" class="close-btn">&times;</button>
                        </div>
                        <form id="register-form">
                            <div class="form-group">
                                <label for="agent-name">Agent Name:</label>
                                <input type="text" id="agent-name" required>
                            </div>
                            <div class="form-group">
                                <label for="agent-endpoint">Endpoint URL:</label>
                                <input type="url" id="agent-endpoint" required placeholder="http://localhost:8001">
                            </div>
                            <div class="form-group">
                                <label for="agent-capabilities">Capabilities (JSON):</label>
                                <textarea id="agent-capabilities" rows="4" placeholder='[{"name": "text-generation", "version": "1.0", "description": "Generate text content"}]'></textarea>
                            </div>
                            <div class="form-actions">
                                <button type="button" id="cancel-register" class="btn btn-secondary">Cancel</button>
                                <button type="submit" class="btn btn-primary">Register Agent</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;

        this.attachEventListeners();
        this.addStyles();
    }

    addStyles() {
        if (document.getElementById('agent-manager-styles')) return;

        const style = document.createElement('style');
        style.id = 'agent-manager-styles';
        style.textContent = `
            .manager-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 25px;
                padding-bottom: 15px;
                border-bottom: 1px solid rgba(255,255,255,0.2);
            }

            .manager-header h2 {
                margin: 0;
                color: #fff;
            }

            .manager-actions {
                display: flex;
                gap: 10px;
            }

            .btn {
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.2s;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                gap: 5px;
            }

            .btn-primary {
                background: #28a745;
                color: white;
            }

            .btn-primary:hover {
                background: #218838;
            }

            .btn-secondary {
                background: rgba(255,255,255,0.2);
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
            }

            .btn-secondary:hover {
                background: rgba(255,255,255,0.3);
            }

            .btn-danger {
                background: #dc3545;
                color: white;
            }

            .btn-danger:hover {
                background: #c82333;
            }

            .agent-stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-bottom: 25px;
            }

            .stat-card {
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.2);
            }

            .stat-number {
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 5px;
            }

            .stat-label {
                font-size: 0.9rem;
                opacity: 0.8;
            }

            .agent-list {
                display: grid;
                gap: 15px;
            }

            .agent-card {
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 20px;
                border: 1px solid rgba(255,255,255,0.2);
                transition: all 0.2s;
            }

            .agent-card:hover {
                background: rgba(255,255,255,0.15);
            }

            .agent-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }

            .agent-title {
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .agent-title h3 {
                margin: 0;
                font-size: 1.2rem;
            }

            .status-badge {
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 500;
                text-transform: uppercase;
            }

            .status-online {
                background: #28a745;
                color: white;
            }

            .status-offline {
                background: #6c757d;
                color: white;
            }

            .status-busy {
                background: #ffc107;
                color: #212529;
            }

            .status-error {
                background: #dc3545;
                color: white;
            }

            .agent-info {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-bottom: 15px;
            }

            .agent-detail {
                font-size: 0.9rem;
            }

            .agent-detail strong {
                display: block;
                margin-bottom: 3px;
                opacity: 0.8;
            }

            .capabilities {
                margin-top: 15px;
            }

            .capability-list {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 10px;
            }

            .capability-tag {
                background: rgba(40, 167, 69, 0.2);
                border: 1px solid rgba(40, 167, 69, 0.4);
                color: #28a745;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.8rem;
            }

            .modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.7);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1000;
            }

            .modal-content {
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                border-radius: 12px;
                width: 90%;
                max-width: 500px;
                max-height: 90vh;
                overflow-y: auto;
                border: 1px solid rgba(255,255,255,0.2);
            }

            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px;
                border-bottom: 1px solid rgba(255,255,255,0.2);
            }

            .modal-header h3 {
                margin: 0;
                color: white;
            }

            .close-btn {
                background: none;
                border: none;
                color: white;
                font-size: 1.5rem;
                cursor: pointer;
                padding: 0;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: background 0.2s;
            }

            .close-btn:hover {
                background: rgba(255,255,255,0.2);
            }

            .form-group {
                margin-bottom: 20px;
            }

            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
                color: white;
            }

            .form-group input,
            .form-group textarea {
                width: 100%;
                padding: 10px;
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 6px;
                background: rgba(255,255,255,0.1);
                color: white;
                font-size: 14px;
                box-sizing: border-box;
            }

            .form-group input::placeholder,
            .form-group textarea::placeholder {
                color: rgba(255,255,255,0.6);
            }

            .form-group input:focus,
            .form-group textarea:focus {
                outline: none;
                border-color: #28a745;
                background: rgba(255,255,255,0.15);
            }

            form {
                padding: 20px;
            }

            .form-actions {
                display: flex;
                gap: 10px;
                justify-content: flex-end;
                margin-top: 20px;
            }

            .error {
                background: rgba(220, 53, 69, 0.2);
                border: 1px solid rgba(220, 53, 69, 0.5);
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                color: #fff;
            }

            .no-agents {
                text-align: center;
                padding: 40px;
                color: rgba(255,255,255,0.7);
            }

            .no-agents h3 {
                margin-bottom: 10px;
            }
        `;
        document.head.appendChild(style);
    }

    attachEventListeners() {
        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.loadAgents();
        });

        // Register button
        document.getElementById('register-btn').addEventListener('click', () => {
            this.showRegisterModal();
        });

        // Modal close handlers
        document.getElementById('close-modal').addEventListener('click', () => {
            this.hideRegisterModal();
        });

        document.getElementById('cancel-register').addEventListener('click', () => {
            this.hideRegisterModal();
        });

        // Registration form
        document.getElementById('register-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.registerAgent();
        });

        // Close modal on backdrop click
        document.getElementById('register-modal').addEventListener('click', (e) => {
            if (e.target.id === 'register-modal') {
                this.hideRegisterModal();
            }
        });
    }

    async loadAgents() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/agents`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            this.agents = await response.json();
            this.renderAgents();
            this.updateStats();
        } catch (error) {
            console.error('Failed to load agents:', error);
            this.renderError('Failed to load agents: ' + error.message);
        }
    }

    renderAgents() {
        const agentList = document.getElementById('agent-list');
        
        if (this.agents.length === 0) {
            agentList.innerHTML = `
                <div class="no-agents">
                    <h3>No Agents Registered</h3>
                    <p>Click "Register Agent" to add your first agent to the fleet.</p>
                </div>
            `;
            return;
        }

        agentList.innerHTML = this.agents.map(agent => `
            <div class="agent-card">
                <div class="agent-header">
                    <div class="agent-title">
                        <h3>${this.escapeHtml(agent.name)}</h3>
                        <span class="status-badge status-${agent.status}">${agent.status}</span>
                    </div>
                    <button class="btn btn-danger btn-sm" onclick="agentManager.removeAgent('${agent.id}')">
                        🗑️ Remove
                    </button>
                </div>
                <div class="agent-info">
                    <div class="agent-detail">
                        <strong>Endpoint:</strong>
                        <span>${this.escapeHtml(agent.endpoint)}</span>
                    </div>
                    <div class="agent-detail">
                        <strong>Last Heartbeat:</strong>
                        <span>${agent.last_heartbeat ? new Date(agent.last_heartbeat).toLocaleString() : 'Never'}</span>
                    </div>
                    <div class="agent-detail">
                        <strong>Created:</strong>
                        <span>${new Date(agent.created_at).toLocaleString()}</span>
                    </div>
                    <div class="agent-detail">
                        <strong>Agent ID:</strong>
                        <span style="font-family: monospace; font-size: 0.8em;">${agent.id}</span>
                    </div>
                </div>
                ${agent.capabilities.length > 0 ? `
                    <div class="capabilities">
                        <strong>Capabilities:</strong>
                        <div class="capability-list">
                            ${agent.capabilities.map(cap => `
                                <span class="capability-tag" title="${this.escapeHtml(cap.description || '')}">${this.escapeHtml(cap.name)} v${this.escapeHtml(cap.version)}</span>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    updateStats() {
        const total = this.agents.length;
        const online = this.agents.filter(agent => agent.status === 'online').length;
        const offline = this.agents.filter(agent => agent.status === 'offline').length;

        document.getElementById('total-agents').textContent = total;
        document.getElementById('online-agents').textContent = online;
        document.getElementById('offline-agents').textContent = offline;
    }

    renderError(message) {
        const agentList = document.getElementById('agent-list');
        agentList.innerHTML = `<div class="error">${this.escapeHtml(message)}</div>`;
    }

    showRegisterModal() {
        document.getElementById('register-modal').style.display = 'flex';
        document.getElementById('agent-name').focus();
    }

    hideRegisterModal() {
        document.getElementById('register-modal').style.display = 'none';
        document.getElementById('register-form').reset();
    }

    async registerAgent() {
        const name = document.getElementById('agent-name').value.trim();
        const endpoint = document.getElementById('agent-endpoint').value.trim();
        const capabilitiesText = document.getElementById('agent-capabilities').value.trim();

        let capabilities = [];
        if (capabilitiesText) {
            try {
                capabilities = JSON.parse(capabilitiesText);
                if (!Array.isArray(capabilities)) {
                    throw new Error('Capabilities must be an array');
                }
            } catch (error) {
                alert('Invalid JSON in capabilities field: ' + error.message);
                return;
            }
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/agents/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name,
                    endpoint,
                    capabilities
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            await response.json();
            this.hideRegisterModal();
            await this.loadAgents(); // Refresh the list
            
        } catch (error) {
            console.error('Failed to register agent:', error);
            alert('Failed to register agent: ' + error.message);
        }
    }

    async removeAgent(agentId) {
        if (!confirm('Are you sure you want to remove this agent?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/agents/${agentId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            await this.loadAgents(); // Refresh the list
            
        } catch (error) {
            console.error('Failed to remove agent:', error);
            alert('Failed to remove agent: ' + error.message);
        }
    }

    startAutoRefresh() {
        // Refresh every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.loadAgents();
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    escapeHtml(text) {
        if (typeof text !== 'string') return text;
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    destroy() {
        this.stopAutoRefresh();
    }
}

// Make it globally available for onclick handlers
window.agentManager = null;

export default AgentManager;