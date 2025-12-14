"""
Phoenix Protocol - Database Models
Built following BUILD_DOSSIER.md specifications
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Guardian(Base):
    """Guardian System Model - Autonomous system monitoring"""
    __tablename__ = "guardians"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    status = Column(String, default="active")  # active, inactive
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    capabilities = Column(JSON, default=list)
    health_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Agent(Base):
    """AI Agent Model - Agent management and tracking"""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, nullable=False, index=True)  # captain, agent
    captain = Column(String, nullable=True, index=True)  # Owner for agents
    status = Column(String, default="online")  # online, offline
    capabilities = Column(JSON, default=list)
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class Mission(Base):
    """Mission Model - Mission control and tracking"""
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String, default="medium")  # low, medium, high, critical
    status = Column(String, default="pending")  # pending, active, completed, failed
    captain = Column(String, nullable=False, index=True)  # Mission owner
    role = Column(String, nullable=False, index=True)  # captain, agent
    assigned_agents = Column(JSON, default=list)  # List of agent IDs
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class VaultLog(Base):
    """Vault Log Model - Activity logging and audit trails"""
    __tablename__ = "vault_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, nullable=False, index=True)  # info, warning, error, critical
    message = Column(Text, nullable=False)
    source = Column(String, nullable=True, index=True)
    log_metadata = Column(JSON, default=dict)  # Renamed from 'metadata' (reserved)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class AdmiralKey(Base):
    """Admiral Key Model - Cryptographic key management"""
    __tablename__ = "admiral_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String, unique=True, nullable=False, index=True)
    public_key = Column(String, nullable=False)
    private_key_encrypted = Column(String, nullable=False)  # Encrypted storage
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)


class FleetShip(Base):
    """Fleet Ship Model - Ship tracking and deployment"""
    __tablename__ = "fleet_ships"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, nullable=False, index=True)  # captain, agent
    status = Column(String, default="online")  # online, offline
    location = Column(String, nullable=True)
    deployment_status = Column(String, default="docked")  # docked, deployed, transit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CaptainMessage(Base):
    """Captain Message Model - Captain-to-captain communication"""
    __tablename__ = "captain_messages"

    id = Column(Integer, primary_key=True, index=True)
    from_captain = Column(String, nullable=False, index=True)
    to_captain = Column(String, nullable=True, index=True)  # None for broadcast
    message = Column(Text, nullable=False)
    priority = Column(String, default="normal")  # low, normal, high, urgent
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
