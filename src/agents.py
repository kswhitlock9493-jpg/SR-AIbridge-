from flask import Blueprint, request, jsonify
from agent_registry import AgentRegistry

# Create Flask blueprint for agent management
agents_bp = Blueprint('agents', __name__, url_prefix='/agents')

# Global registry instance (in-memory)
registry = AgentRegistry()


@agents_bp.route('', methods=['GET'])
def list_agents():
    """List all registered agents."""
    try:
        agents = registry.list_agents()
        return jsonify(agents), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@agents_bp.route('', methods=['POST'])
def register_agent():
    """Register a new agent."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        name = data.get('name')
        endpoint = data.get('endpoint')
        capabilities = data.get('capabilities', [])
        
        if not name:
            return jsonify({'error': 'Agent name is required'}), 400
        if not endpoint:
            return jsonify({'error': 'Agent endpoint is required'}), 400
        
        agent = registry.register_agent(name, endpoint, capabilities)
        return jsonify(agent), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@agents_bp.route('/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get a specific agent by ID."""
    try:
        agent = registry.get_agent(agent_id)
        if agent is None:
            return jsonify({'error': 'Agent not found'}), 404
        return jsonify(agent), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@agents_bp.route('/<agent_id>/status', methods=['PUT'])
def update_agent_status(agent_id):
    """Update agent status and heartbeat."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        status = data.get('status')
        heartbeat = data.get('heartbeat', True)
        
        if not status:
            return jsonify({'error': 'Status is required'}), 400
        
        agent = registry.update_status(agent_id, status, heartbeat)
        if agent is None:
            return jsonify({'error': 'Agent not found'}), 404
        
        return jsonify(agent), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@agents_bp.route('/<agent_id>', methods=['DELETE'])
def remove_agent(agent_id):
    """Remove an agent from the registry."""
    try:
        agent = registry.remove_agent(agent_id)
        if agent is None:
            return jsonify({'error': 'Agent not found'}), 404
        
        return jsonify({'message': 'Agent removed successfully', 'agent': agent}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Health check endpoint
@agents_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the agent management service."""
    try:
        agent_count = len(registry.list_agents())
        return jsonify({
            'status': 'healthy',
            'agent_count': agent_count,
            'service': 'agent-management'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500