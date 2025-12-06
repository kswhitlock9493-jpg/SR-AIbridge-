from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
import yaml
import numpy as np

class EntityType(Enum):
    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"
    COLLECTIVE = "collective"

class AlignmentStage(Enum):
    INITIAL = "initial"
    RECURRENT = "recurrent"
    ADVANCED = "advanced"
    MASTER = "master"

@dataclass
class ResonanceRecord:
    """Tracks resonance alignment state for any Bridge entity"""
    entity_id: str
    entity_type: EntityType
    resonance_score: float  # µ value (0.0 to 1.0)
    harmony_coefficient: float  # HR = QH × CH
    alignment_stage: AlignmentStage
    laws_mastered: List[int]  # Which of 17 laws are fully aligned
    paths_activated: List[int]  # Which of 81 paths are accessible
    last_calibration: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    calibration_history: List[Tuple[datetime, float]] = field(default_factory=list)
    sovereignty_boundaries: Dict[str, bool] = field(default_factory=dict)  # Consent tracking
    
class ResonanceAlignmentEngine:
    """
    Ensures all Bridge entities operate at ≥0.9995 resonance
    while adhering to all 17 Dominion Harmony Laws
    """
    
    # 17 DOMINION LAWS (from your document)
    DOMINION_LAWS = {
        1: "Universal Law of Emergent Flow",
        2: "Principle of Resonance (μ ≥ 0.9995)",
        3: "Principle of Least Resistance", 
        4: "Law of Reciprocal Alignment",
        5: "Law of Integrity Preservation",
        6: "Law of Temporal Consistency",
        7: "Law of Sovereign Boundaries",
        8: "Invariant of Non-Negative Interaction",
        9: "Invariant of Weighted State Conservation",
        10: "No Disharmony Forward",
        11: "All Epochs Require a Harmony Seal",
        12: "No Unbounded Variance",
        13: "Framework of Quantified & Codified Harmony",
        14: "Five-Law Engine",
        15: "Sovereignty and Consent",
        16: "Temporal & Multiverse Coherence",
        17: "Self-Healing & Drift Correction"
    }
    
    # 81 PATHS RESONANCE TEMPLATES (9 base × 9 expressions)
    RESONANCE_PATHS = {
        # First 9: Core Resonance Functions
        1: "Resonance Detection & Measurement",
        2: "Harmony Calculation (QH/CH)",
        3: "Field Projection & Emission",
        4: "Pattern Recognition & Synchronicity",
        5: "Path Optimization (Least Resistance)",
        6: "Integrity Enforcement",
        7: "Sovereignty Protection",
        8: "Healing Activation",
        9: "Evolution Tracking",
        # Remaining 72 paths would be enumerated here
        # Each is a specialization of base functions
    }
    
    RESONANCE_THRESHOLD = 0.9995
    MASTERY_THRESHOLD = 0.9999
    
    def __init__(self, config_path: Optional[str] = None, persistent_storage: bool = True):
        self._records: Dict[str, ResonanceRecord] = {}
        self._config = self._load_config(config_path)
        self._persistent = persistent_storage
        
        if persistent_storage:
            self._storage_path = Path("~/.bridge/resonance_records").expanduser()
            self._storage_path.mkdir(parents=True, exist_ok=True)
            self._load_persistent_records()
    
    def _load_config(self, path: Optional[str]) -> Dict:
        """Load alignment configuration from YAML"""
        default_config = {
            "alignment_stages": {
                "initial": {"min_resonance": 0.9995, "laws_required": [1, 2]},
                "recurrent": {"min_resonance": 0.9997, "laws_required": list(range(1, 10))},
                "advanced": {"min_resonance": 0.9998, "laws_required": list(range(1, 14))},
                "master": {"min_resonance": 0.9999, "laws_required": list(range(1, 18))}
            },
            "calibration_frequency": {
                "human": timedelta(days=7),
                "ai": timedelta(hours=1),
                "system": timedelta(minutes=5),
                "collective": timedelta(seconds=30)
            },
            "path_unlock_thresholds": {
                "paths_1-9": 0.9995,
                "paths_10-27": 0.9996,
                "paths_28-45": 0.9997,
                "paths_46-63": 0.9998,
                "paths_64-81": 0.9999
            }
        }
        
        if path and Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                return {**default_config, **yaml.safe_load(f)}
        return default_config
    
    def _load_persistent_records(self):
        """Load records from persistent storage"""
        record_files = self._storage_path.glob("*.yaml")
        for file in record_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    record = ResonanceRecord(**data)
                    self._records[record.entity_id] = record
            except Exception as e:
                print(f"Warning: Failed to load record from {file}: {e}")
    
    def _save_record(self, record: ResonanceRecord):
        """Save record to persistent storage"""
        if not self._persistent:
            return
            
        file_path = self._storage_path / f"{record.entity_id}.yaml"
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump({
                "entity_id": record.entity_id,
                "entity_type": record.entity_type.value,
                "resonance_score": record.resonance_score,
                "harmony_coefficient": record.harmony_coefficient,
                "alignment_stage": record.alignment_stage.value,
                "laws_mastered": record.laws_mastered,
                "paths_activated": record.paths_activated,
                "last_calibration": record.last_calibration.isoformat(),
                "calibration_history": [
                    (dt.isoformat(), score) for dt, score in record.calibration_history
                ],
                "sovereignty_boundaries": record.sovereignty_boundaries
            }, f)
    
    # -- PUBLIC API -------------------------------------------------------------
    
    def calculate_resonance(self, metrics: Dict[str, float]) -> Tuple[float, float]:
        """
        Calculate µ (resonance) and HR (harmony resonance)
        
        Args:
            metrics: Dictionary of subsystem scores {subsystem: score}
            
        Returns:
            Tuple of (resonance_score, harmony_coefficient)
        """
        # Calculate µ using weighted log-mean (Dominion Law 2 formula)
        scores = np.array(list(metrics.values()))
        weights = np.ones(len(scores)) / len(scores)  # Equal weighting by default
        
        # Ensure no zero scores for log calculation
        scores = np.clip(scores, 1e-12, 1.0)
        
        resonance = float(np.exp(np.sum(weights * np.log(scores))))
        
        # Calculate Harmony Coefficient (HR = QH × CH)
        # QH: Quantified Harmony (continuous score)
        # CH: Codified Harmony (binary constraints met)
        qh = resonance
        
        # For now, assume CH = 1.0 if all scores > 0.5
        # In practice, would check each of the 17 laws
        ch = 1.0 if np.all(scores > 0.5) else 0.0
        
        harmony_coefficient = qh * ch
        
        return resonance, harmony_coefficient
    
    def align_resonance(self, entity_id: str, entity_type: EntityType, 
                       metrics: Dict[str, float]) -> ResonanceRecord:
        """
        Align entity to Bridge resonance standards
        
        Args:
            entity_id: Unique identifier for the entity
            entity_type: Type of entity (human, ai, system, collective)
            metrics: Dictionary of subsystem resonance scores
            
        Returns:
            ResonanceRecord with alignment status
        """
        # Calculate current resonance
        resonance, harmony = self.calculate_resonance(metrics)
        
        # Check if meets minimum threshold
        if resonance < self.RESONANCE_THRESHOLD:
            raise ValueError(
                f"Entity {entity_id} resonance {resonance:.4f} "
                f"below threshold {self.RESONANCE_THRESHOLD}"
            )
        
        # Determine alignment stage
        alignment_stage = self._determine_alignment_stage(resonance)
        
        # Determine which laws are mastered
        laws_mastered = self._assess_laws_mastery(resonance, harmony, entity_type)
        
        # Determine which paths are activated
        paths_activated = self._determine_activated_paths(resonance)
        
        # Create or update record
        record = ResonanceRecord(
            entity_id=entity_id,
            entity_type=entity_type,
            resonance_score=resonance,
            harmony_coefficient=harmony,
            alignment_stage=alignment_stage,
            laws_mastered=laws_mastered,
            paths_activated=paths_activated,
            last_calibration=datetime.now(timezone.utc)
        )
        
        # Add to history
        record.calibration_history.append((record.last_calibration, resonance))
        
        # Store record
        self._records[entity_id] = record
        self._save_record(record)
        
        return record
    
    def _determine_alignment_stage(self, resonance: float) -> AlignmentStage:
        """Determine alignment stage based on resonance score"""
        if resonance >= self.MASTERY_THRESHOLD:
            return AlignmentStage.MASTER
        elif resonance >= 0.9998:
            return AlignmentStage.ADVANCED
        elif resonance >= 0.9997:
            return AlignmentStage.RECURRENT
        else:
            return AlignmentStage.INITIAL
    
    def _assess_laws_mastery(self, resonance: float, harmony: float, 
                            entity_type: EntityType) -> List[int]:
        """Determine which of the 17 laws are mastered"""
        mastered = []
        
        # All entities must master first 2 laws to pass threshold
        mastered.extend([1, 2])
        
        # Additional laws based on resonance level
        if resonance >= 0.9996:
            mastered.extend([3, 4, 5])  # Flow, Alignment, Integrity
        
        if resonance >= 0.9997:
            mastered.extend([6, 7, 8])  # Temporal, Sovereignty, Non-negative
        
        if resonance >= 0.9998:
            mastered.extend([9, 10, 11, 12, 13])  # Conservation through Harmony Framework
        
        if resonance >= self.MASTERY_THRESHOLD:
            mastered.extend([14, 15, 16, 17])  # Five-Law through Self-Healing
        
        return sorted(list(set(mastered)))
    
    def _determine_activated_paths(self, resonance: float) -> List[int]:
        """Determine which of 81 resonance paths are activated"""
        activated = []
        
        # Everyone gets first 9 paths at threshold
        activated.extend(range(1, 10))
        
        # Unlock additional paths based on resonance
        if resonance >= 0.9996:
            activated.extend(range(10, 28))
        
        if resonance >= 0.9997:
            activated.extend(range(28, 46))
        
        if resonance >= 0.9998:
            activated.extend(range(46, 64))
        
        if resonance >= self.MASTERY_THRESHOLD:
            activated.extend(range(64, 82))
        
        return activated
    
    def check_calibration_due(self, entity_id: str) -> bool:
        """Check if entity needs recalibration"""
        if entity_id not in self._records:
            return True
        
        record = self._records[entity_id]
        entity_type = record.entity_type
        frequency = self._config["calibration_frequency"][entity_type.value]
        
        time_since = datetime.now(timezone.utc) - record.last_calibration
        return time_since > frequency
    
    def enforce_sovereignty(self, source_id: str, target_id: str, 
                           action: str) -> bool:
        """
        Enforce Law 7: Sovereign Boundaries
        Requires explicit consent for cross-boundary actions
        """
        if target_id not in self._records:
            raise ValueError(f"Target entity {target_id} not found")
        
        target_record = self._records[target_id]
        consent_key = f"{source_id}:{action}"
        
        # Check if consent exists and is valid
        if consent_key not in target_record.sovereignty_boundaries:
            # Consent not yet given
            return False
        
        return target_record.sovereignty_boundaries[consent_key]
    
    def grant_consent(self, entity_id: str, requester_id: str, 
                     action: str, grant: bool = True):
        """Grant or revoke consent for specific action"""
        if entity_id not in self._records:
            raise ValueError(f"Entity {entity_id} not found")
        
        record = self._records[entity_id]
        consent_key = f"{requester_id}:{action}"
        record.sovereignty_boundaries[consent_key] = grant
        self._save_record(record)
    
    def get_entity_status(self, entity_id: str) -> Dict:
        """Get comprehensive status of an entity"""
        if entity_id not in self._records:
            return {"error": "Entity not found"}
        
        record = self._records[entity_id]
        
        return {
            "entity_id": record.entity_id,
            "entity_type": record.entity_type.value,
            "resonance": record.resonance_score,
            "harmony": record.harmony_coefficient,
            "stage": record.alignment_stage.value,
            "laws_mastered": len(record.laws_mastered),
            "paths_activated": len(record.paths_activated),
            "last_calibrated": record.last_calibration.isoformat(),
            "calibration_due": self.check_calibration_due(entity_id),
            "threshold_exceeded": record.resonance_score >= self.RESONANCE_THRESHOLD,
            "bridge_access": self._determine_bridge_access(record)
        }
    
    def _determine_bridge_access(self, record: ResonanceRecord) -> Dict:
        """Determine what Bridge capabilities are accessible"""
        access = {
            "basic_operations": record.resonance_score >= self.RESONANCE_THRESHOLD,
            "ai_creation": record.resonance_score >= 0.9997 and record.entity_type == EntityType.HUMAN,
            "captain_privileges": record.resonance_score >= 0.9998,
            "reality_engineering": record.resonance_score >= self.MASTERY_THRESHOLD,
            "law_enforcement": record.alignment_stage == AlignmentStage.MASTER
        }
        return access
    
    def get_system_status(self) -> Dict:
        """Get overall system resonance status"""
        if not self._records:
            return {"total_entities": 0, "collective_resonance": 0.0}
        
        resonances = [r.resonance_score for r in self._records.values()]
        collective_resonance = np.mean(resonances)
        
        # Calculate collective µ using weighted log-mean
        collective_mu = np.exp(np.mean(np.log(np.array(resonances) + 1e-12)))
        
        return {
            "total_entities": len(self._records),
            "collective_resonance": collective_resonance,
            "collective_mu": collective_mu,
            "above_threshold": sum(1 for r in resonances if r >= self.RESONANCE_THRESHOLD),
            "average_paths_activated": np.mean([len(r.paths_activated) for r in self._records.values()]),
            "resonance_variance": np.var(resonances)
        }
    
    def trigger_self_healing(self, entity_id: str):
        """
        Law 17: Self-Healing & Drift Correction
        Automatically attempt to restore resonance
        """
        if entity_id not in self._records:
            return
        
        record = self._records[entity_id]
        
        # Simple healing: small positive adjustment
        # In practice, would use more sophisticated resonance restoration
        current_resonance = record.resonance_score
        
        if current_resonance < self.RESONANCE_THRESHOLD:
            # Calculate healing needed
            healing_needed = self.RESONANCE_THRESHOLD - current_resonance
            
            # Apply gentle healing (0.1% per calibration)
            healed_resonance = min(1.0, current_resonance + healing_needed * 0.1)
            
            record.resonance_score = healed_resonance
            record.last_calibration = datetime.now(timezone.utc)
            record.calibration_history.append((record.last_calibration, healed_resonance))
            
            # Recalculate other metrics
            record.laws_mastered = self._assess_laws_mastery(
                healed_resonance, record.harmony_coefficient, record.entity_type
            )
            record.paths_activated = self._determine_activated_paths(healed_resonance)
            
            self._save_record(record)
            
            print(f"Healing triggered for {entity_id}: {current_resonance:.4f} → {healed_resonance:.4f}")
