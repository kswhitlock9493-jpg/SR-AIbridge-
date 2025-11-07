"""
Authentication Routes for Keyless Security
Handles ephemeral session establishment and dynamic key generation
"""

from flask import Blueprint, request, jsonify

try:
    from ...src.keyless_auth import get_keyless_handler
except (ImportError, ValueError):
    # Fallback if relative import fails (e.g., when running standalone)
    try:
        from bridge_backend.src.keyless_auth import get_keyless_handler
    except ImportError:
        get_keyless_handler = None

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/session', methods=['POST'])
def establish_session():
    """
    Establish ephemeral session with dynamic key generation
    
    POST /auth/session
    Body: {
        "requestType": "ephemeral_session",
        "keyGenerationType": "dynamic"
    }
    
    Returns:
    {
        "authenticated": true,
        "sessionId": "...",
        "keyType": "ephemeral",
        "staticKeysUsed": false,
        "session": {...}
    }
    """
    if get_keyless_handler is None:
        return jsonify({
            'authenticated': False,
            'capability': 'testing',
            'message': 'Keyless auth module not available',
            'staticKeysUsed': False
        }), 200
    
    try:
        data = request.get_json() or {}
        request_type = data.get('requestType', 'ephemeral_session')
        key_gen_type = data.get('keyGenerationType', 'dynamic')
        
        # Get keyless handler
        handler = get_keyless_handler()
        
        # Establish ephemeral session
        result = handler.establish_ephemeral_session()
        
        # Format response for frontend
        return jsonify({
            'authenticated': result['authenticated'],
            'sessionId': result['session']['session_id'],
            'keyType': 'ephemeral',
            'staticKeysUsed': False,
            'session': result['session'],
            'securityModel': result['security_model'],
            'advantages': result['advantages']
        }), 200
        
    except Exception as e:
        return jsonify({
            'authenticated': False,
            'error': str(e),
            'capability': 'testing',
            'staticKeysUsed': False
        }), 200


@auth_bp.route('/capability', methods=['GET'])
def check_capability():
    """
    Check dynamic key generation capability
    
    GET /auth/capability
    
    Returns:
    {
        "capable": true,
        "authModel": "keyless_ephemeral_sessions",
        "staticKeysExist": false
    }
    """
    if get_keyless_handler is None:
        return jsonify({
            'capable': False,
            'authModel': 'pending',
            'staticKeysExist': False,
            'message': 'Keyless auth module not available'
        }), 200
    
    try:
        handler = get_keyless_handler()
        capable = handler.verify_dynamic_key_generation()
        status = handler.get_status()
        
        return jsonify({
            'capable': capable,
            'authModel': status['auth_model'],
            'staticKeysExist': status['static_keys_exist'],
            'activeSessions': status['active_sessions'],
            'securityAdvantages': status['security_advantages']
        }), 200
        
    except Exception as e:
        return jsonify({
            'capable': False,
            'error': str(e),
            'staticKeysExist': False
        }), 500


@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """
    Get authentication system status
    
    GET /auth/status
    
    Returns complete status of keyless auth system
    """
    if get_keyless_handler is None:
        return jsonify({
            'authModel': 'pending',
            'staticKeysExist': False,
            'message': 'Keyless auth module not available'
        }), 200
    
    try:
        handler = get_keyless_handler()
        status = handler.get_status()
        
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'authModel': 'error',
            'staticKeysExist': False
        }), 500


# Export blueprint
def init_auth_routes(app):
    """Initialize auth routes on Flask app"""
    app.register_blueprint(auth_bp)
    return auth_bp
