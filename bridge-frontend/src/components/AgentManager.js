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
            /* ... rest of style unchanged ... */
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
        const confirmed = window.confirm('Are you sure?');
        if (!confirmed) return;

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
