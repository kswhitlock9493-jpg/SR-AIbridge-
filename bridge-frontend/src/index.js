import AgentManager from './components/AgentManager.js';

// Initialize the agent manager
document.addEventListener('DOMContentLoaded', () => {
    const root = document.getElementById('root');
    window.agentManager = new AgentManager(root);
    window.agentManager.init();
});