"""
SR-AIbridge In-Memory Backend Demo Seeder

This script demonstrates how to populate the in-memory backend with demo data
by making HTTP requests to the running backend server.

Usage:
    1. Start the backend: uvicorn main:app --reload
    2. Run this script: python seed.py
    3. Visit http://localhost:8000/status to verify seeded data

The backend automatically seeds data on startup, but this script shows
how you could add additional data programmatically.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

async def test_and_seed_data():
    """Test the API endpoints and add some additional demo data"""
    
    try:
        async with aiohttp.ClientSession() as session:
            print("🚀 Testing SR-AIbridge In-Memory Backend")
            
            # Test status endpoint
            print("\n📊 Checking status...")
            async with session.get(f"{API_BASE}/status") as resp:
                if resp.status == 200:
                    status = await resp.json()
                    print(f"✅ Status: {status['agents_online']} agents online, {status['active_missions']} active missions")
                else:
                    print("❌ Backend not running. Start with: uvicorn main:app --reload")
                    return
            
            # Test agents endpoint
            print("\n🤖 Checking agents...")
            async with session.get(f"{API_BASE}/agents") as resp:
                if resp.status == 200:
                    agents = await resp.json()
                    print(f"✅ Found {len(agents)} agents")
                    for agent in agents:
                        print(f"   - {agent['name']} ({agent['status']})")
            
            # Add a new agent
            print("\n➕ Adding demo agent...")
            new_agent = {
                "name": "Agent Gamma",
                "endpoint": "http://agent-gamma:8003",
                "capabilities": [
                    {"name": "logistics", "version": "1.2", "description": "Supply chain optimization"},
                    {"name": "coordination", "version": "2.0", "description": "Multi-agent task coordination"}
                ]
            }
            async with session.post(f"{API_BASE}/agents", json=new_agent) as resp:
                if resp.status == 200:
                    agent = await resp.json()
                    print(f"✅ Added Agent: {agent['name']} (ID: {agent['id']})")
            
            # Test missions endpoint
            print("\n🚀 Checking missions...")
            async with session.get(f"{API_BASE}/missions") as resp:
                if resp.status == 200:
                    missions = await resp.json()
                    print(f"✅ Found {len(missions)} missions")
                    for mission in missions:
                        print(f"   - {mission['title']} ({mission['status']})")
            
            # Add a new mission
            print("\n➕ Adding demo mission...")
            new_mission = {
                "title": "Nebula Exploration",
                "description": "Investigate anomalous readings from the Helix Nebula",
                "status": "planning",
                "priority": "high"
            }
            async with session.post(f"{API_BASE}/missions", json=new_mission) as resp:
                if resp.status == 200:
                    mission = await resp.json()
                    print(f"✅ Added Mission: {mission['title']} (ID: {mission['id']})")
            
            # Test vault logs
            print("\n📜 Checking vault logs...")
            async with session.get(f"{API_BASE}/vault/logs") as resp:
                if resp.status == 200:
                    logs = await resp.json()
                    print(f"✅ Found {len(logs)} vault logs")
                    for log in logs[:3]:  # Show first 3
                        print(f"   - {log['agent_name']}: {log['action']} ({log['log_level']})")
            
            # Add a vault log
            print("\n➕ Adding demo vault log...")
            new_log = {
                "agent_name": "Agent Gamma",
                "action": "system_check",
                "details": "Performed routine system diagnostics - all systems nominal",
                "log_level": "info"
            }
            async with session.post(f"{API_BASE}/vault/logs", json=new_log) as resp:
                if resp.status == 200:
                    log = await resp.json()
                    print(f"✅ Added Vault Log: {log['action']} by {log['agent_name']}")
            
            # Test captain messages
            print("\n💬 Checking captain messages...")
            async with session.get(f"{API_BASE}/captains/messages") as resp:
                if resp.status == 200:
                    messages = await resp.json()
                    print(f"✅ Found {len(messages)} captain messages")
                    for msg in messages[:2]:  # Show first 2
                        print(f"   - {msg['from_']} → {msg['to']}: {msg['message'][:50]}...")
            
            # Send a captain message
            print("\n➕ Sending demo captain message...")
            new_message = {
                "from_": "Captain Nova",
                "to": "Admiral Kyle",
                "message": "Requesting permission to investigate the nebula anomaly. My sensors are picking up unusual energy signatures."
            }
            async with session.post(f"{API_BASE}/captains/send", json=new_message) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✅ Sent message from {result['stored']['from_']} to {result['stored']['to']}")
            
            # Test armada status
            print("\n🗺️ Checking armada fleet...")
            async with session.get(f"{API_BASE}/armada/status") as resp:
                if resp.status == 200:
                    fleet = await resp.json()
                    print(f"✅ Found {len(fleet)} ships in fleet")
                    for ship in fleet:
                        print(f"   - {ship['name']}: {ship['status']} at {ship['location']}")
            
            # Final status check
            print("\n📊 Final status check...")
            async with session.get(f"{API_BASE}/status") as resp:
                if resp.status == 200:
                    status = await resp.json()
                    print(f"✅ Final Status:")
                    print(f"   - Agents Online: {status['agents_online']}")
                    print(f"   - Active Missions: {status['active_missions']}")
                    print(f"   - Fleet Ships: {status['fleet_count']}")
                    print(f"   - Total Agents: {status['total_agents']}")
                    print(f"   - Total Missions: {status['total_missions']}")
                    print(f"   - Vault Logs: {status['vault_logs']}")
            
            print("\n🎉 Demo seeding complete!")
            print("💡 Visit http://localhost:8000/docs for interactive API documentation")
            print("🌐 Frontend should now have data to display")

    except aiohttp.ClientError as e:
        print(f"❌ Connection error: {e}")
        print("Make sure the backend is running with: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("Installing aiohttp if needed...")
    import subprocess
    import sys
    try:
        import aiohttp
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
        import aiohttp
    
    asyncio.run(test_and_seed_data())