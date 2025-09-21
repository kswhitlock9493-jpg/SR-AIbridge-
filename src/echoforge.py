import asyncio
import json
import random
import time
import hashlib
from typing import Dict, List, Any, Tuple
import os

def atomicappendjsonl(path: str, obj: dict):
    line = json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '\n'
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o640)
    try:
        os.write(fd, line.encode('utf-8'))
        os.fsync(fd)
    finally:
        os.close(fd)

def fingerprint_event(event: Dict[str, Any]) -> Dict[str, Any]:
    payload = event.get('payload', {})
    reason = str(payload.get('reason', '')).lower()
    summary = str(payload.get('summary', '')).lower() if event.get('payload') else ''
    source = event.get('agent') or event.get('bridge_id') or 'unknown'
    ts = event.get('timestamp', str(time.time()))
    style = 'unknown'
    if 'corrupt' in reason or 'invalid' in reason or 'malformed' in reason:
        style = 'corruption'
    elif 'timeout' in reason or 'timed out' in reason:
        style = 'latency'
    elif 'auth' in reason or 'signature' in reason or 'forged' in reason:
        style = 'auth'
    elif 'permission' in reason or 'unauthorized' in reason:
        style = 'access'
    elif 'unknown' in reason:
        style = 'unknown_vector'
    elif 'simulated_failure' in reason:
        style = 'sim_failure'
    sev = 0.1
    if style in ('auth', 'access'):
        sev = 0.9
    elif style in ('corruption', 'unknown_vector'):
        sev = 0.7
    elif style == 'latency':
        sev = 0.4
    canonical = f'{source}|{ts}|{reason}|{summary}'
    h = hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:12]
    return {
        'fingerprint_id': f'echoforge_{h}',
        'style': style,
        'severity': sev,
        'reason': reason,
        'summary': summary,
        'origin': source,
        'ts': ts,
    }

def synthesize_agent_specs(fingerprint: Dict[str, Any], k: int = 3) -> List[Dict[str, Any]]:
    specs = []
    base = fingerprint['fingerprint_id']
    style = fingerprint['style']
    sev = fingerprint['severity']
    for i in range(k):
        name = f'Echo_{base}_{i+1}'
        if style == 'corruption':
            role = random.choice(['integrity_scanner', 'payload_sanitizer', 'quarantine_agent'])
            caps = ['input.validation', 'payload.sanitization', 'quarantine.routing']
            conf = 0.85 - (i * 0.05)
            resp = f'{0.5 + i * 0.2}s'
        elif style == 'auth':
            role = random.choice(['sig_verifier', 'replay_detector', 'key_rotary'])
            caps = ['crypto.verify', 'replay.protection', 'key.rotation']
            conf = 0.9 - (i * 0.03)
            resp = f'{0.6 + i * 0.2}s'
        elif style == 'latency':
            role = random.choice(['timeout_probe', 'latency_mitigator', 'route_fallback'])
            caps = ['latency.probing', 'queue.routing', 'backoff.control']
            conf = 0.75 - (i * 0.05)
            resp = f'{0.8 + i * 0.25}s'
        else:
            role = random.choice(['forensic_logger', 'probe_responder', 'adaptive_router'])
            caps = ['forensics.capture', 'probe.respond', 'adaptive.routing']
            conf = 0.7 - (i * 0.04)
            resp = f'{1.0 + i * 0.2}s'
        spec = {
            'agent_name': name,
            'preferred_task_types': [role],
            'capabilities': caps,
            'confidence_scores': {role: conf},
            'response_time_estimate': resp,
            'meta': {'created_by': 'echoforge', 'fingerprint': fingerprint['fingerprint_id'], 'style': style, 'severity': sev},
        }
        specs.append(spec)
    return specs

async def deploy_echo_agents(bridge, specs: List[Dict[str, Any]], ttl_seconds: int = 60):
    registered = []
    for s in specs:
        try:
            bridge.register_ai(s)
            registered.append(s['agent_name'])
            await bridge.bridge_emit('echoforge_agent_registered', s['agent_name'], 'echoforge', {'meta': s.get('meta', {})})
        except Exception as ex:
            await bridge.bridge_emit('echoforge_agent_register_failed', None, 'echoforge', {'spec': s, 'error': str(ex)})
    for name in registered:
        probe = {
            'task_id': f'echoprobe::{name}::{int(time.time())}',
            'origin': 'echoforge',
            'destination': name,
            'summary': f'Probe task for {name}',
            'task_type': 'forensic_probe',
            'required_capabilities': [],
            'content': {'probe_for': 'vector_analysis'},
        }
        try:
            await bridge.post_task(probe)
        except Exception:
            await bridge.bridge_emit('echoforge_probe_post_failed', probe['task_id'], name, {'reason': 'post_failed'})
    async def cleanup():
        await asyncio.sleep(ttl_seconds)
        for name in registered:
            try:
                if hasattr(bridge, 'adapters') and name in bridge.adapters:
                    bridge.adapters.pop(name, None)
                    bridge.registry.pop(name, None)
                    await bridge.bridge_emit('echoforge_agent_unregistered', None, name, {'reason': 'ttl_expired'})
            except Exception:
                pass
    asyncio.create_task(cleanup())
    return registered

def archive_echoforge_event(vault_path: str, fingerprint: Dict[str, Any], specs: List[Dict[str, Any]], outcome: Dict[str, Any] = None):
    artifact = {
        'ts': time.time(),
        'type': 'echoforge_event',
        'fingerprint': fingerprint,
        'created_agents': [s['agent_name'] for s in specs],
        'specs': specs,
        'outcome_summary': outcome or {},
    }
    atomicappendjsonl(vault_path, artifact)
    return artifact

async def echoforge_handle_event(bridge, event: Dict[str, Any], *, vault_path: str = 'vault/echoforge_events.jsonl', k: int = 3, ttl_seconds: int = 60):
    fp = fingerprint_event(event)
    specs = synthesize_agent_specs(fp, k=k)
    artifact = {
        'phase': 'predeploy',
        'fingerprint': fp,
        'specs': specs,
        'origin_event': event,
    }
    atomicappendjsonl(vault_path, artifact)
    registered = await deploy_echo_agents(bridge, specs, ttl_seconds=ttl_seconds)
    post = {
        'phase': 'postdeploy',
        'fingerprint_id': fp['fingerprint_id'],
        'registered_agents': registered,
        'timestamp': time.time(),
    }
    atomicappendjsonl(vault_path, post)
    await bridge.bridge_emit('echoforge_deployed', None, 'echoforge', {'fingerprint': fp, 'agents': registered})
    return {'fingerprint': fp, 'registered': registered}