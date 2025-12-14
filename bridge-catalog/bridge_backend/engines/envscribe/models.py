"""
EnvScribe Data Models
Defines data structures for environment intelligence system
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum


class VerificationStatus(Enum):
    """Status of environment variable verification"""
    VERIFIED = "✅"  # Variable exists and matches
    MISSING = "🟥"   # Variable doesn't exist
    PARTIAL = "🟨"   # Variable exists but no value
    DRIFTED = "⚠️"   # Variable exists but values differ


class VariableScope(Enum):
    """Deployment scope for environment variables"""
    RENDER = "Render"
    NETLIFY = "Netlify"
    GITHUB = "GitHub"
    ALL = "All"


class VariableType(Enum):
    """Type classification for environment variables"""
    URL = "URL"
    SECRET = "Secret"
    STRING = "String"
    BOOL = "Bool"
    INT = "Int"


@dataclass
class EnvVariable:
    """Represents a single environment variable"""
    name: str
    scope: List[str]
    var_type: str
    default: Optional[str] = None
    description: str = ""
    verified: str = VerificationStatus.VERIFIED.value
    value: Optional[str] = None
    required: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class WebhookDefinition:
    """Represents a webhook endpoint"""
    path: str
    engine: str
    description: str = ""
    method: str = "POST"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class EnvScribeSummary:
    """Summary of environment scan results"""
    total_keys: int = 0
    verified: int = 0
    missing_in_render: int = 0
    missing_in_netlify: int = 0
    missing_in_github: int = 0
    drifted: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class EnvScribeReport:
    """Complete EnvScribe scan report"""
    summary: EnvScribeSummary
    variables: List[EnvVariable] = field(default_factory=list)
    missing_in_render: List[str] = field(default_factory=list)
    missing_in_netlify: List[str] = field(default_factory=list)
    missing_in_github: List[str] = field(default_factory=list)
    drifted: Dict[str, Dict[str, str]] = field(default_factory=dict)
    webhooks: List[WebhookDefinition] = field(default_factory=list)
    certified: bool = False
    certificate_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "summary": self.summary.to_dict(),
            "variables": [v.to_dict() for v in self.variables],
            "missing_in_render": self.missing_in_render,
            "missing_in_netlify": self.missing_in_netlify,
            "missing_in_github": self.missing_in_github,
            "drifted": self.drifted,
            "webhooks": [w.to_dict() for w in self.webhooks],
            "certified": self.certified,
            "certificate_id": self.certificate_id
        }
