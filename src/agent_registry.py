import uuid
import datetime

class AgentRegistry:
    def __init__(self):
        # dictionary of agents: {id: {...agent data...}}
        self.agents = {}

    def register_agent(self, name, endpoint, capabilities):
        agent_id = str(uuid.uuid4())
        self.agents[agent_id] = {
            "id": agent_id,
            "name": name,
            "endpoint": endpoint,
            "capabilities": capabilities or [],
            "status": "offline",  # default until heartbeat arrives
            "created_at": datetime.datetime.utcnow().isoformat(),
            "last_heartbeat": None,
        }
        return self.agents[agent_id]

    def list_agents(self):
        return list(self.agents.values())

    def get_agent(self, agent_id):
        return self.agents.get(agent_id)

    def update_status(self, agent_id, status, heartbeat=True):
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = status
            if heartbeat:
                self.agents[agent_id]["last_heartbeat"] = datetime.datetime.utcnow().isoformat()
            return self.agents[agent_id]
        return None

    def remove_agent(self, agent_id):
        return self.agents.pop(agent_id, None)