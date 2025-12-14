from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal

# Tiers
Tier = Literal["free", "pro", "admiral"]

class AutonomySettings(BaseModel):
    enabled: bool = False
    max_hours_per_day: int = 0   # 0 = none
    modes: List[Literal["screen", "connector", "hybrid"]] = []

class LocationSettings(BaseModel):
    share: Literal["none", "approximate", "precise"] = "none"

class ScreenSettings(BaseModel):
    share: bool = False
    mirror: bool = False
    overlay: bool = False

class VoiceSettings(BaseModel):
    stt: bool = False
    tts: bool = False

class DataSettings(BaseModel):
    email: bool = False
    drive: bool = False
    docs: bool = False
    chats: bool = False

class LoggingSettings(BaseModel):
    level: Literal["minimal","standard","verbose"] = "standard"
    retention_days: int = 30

class PushSettings(BaseModel):
    enabled: bool = False
    alerts: bool = False
    updates: bool = False
    reminders: bool = False

class PermissionSettings(BaseModel):
    captain: str = Field(..., min_length=1)
    tier: Tier = "free"
    autonomy: AutonomySettings = AutonomySettings()
    location: LocationSettings = LocationSettings()
    screen: ScreenSettings = ScreenSettings()
    voice: VoiceSettings = VoiceSettings()
    data: DataSettings = DataSettings()
    logging: LoggingSettings = LoggingSettings()
    push: PushSettings = PushSettings()
    consent_version: str = "v1.0"
    consent_given: bool = False
