"""
EntangleCore - Quantum Mechanics Engine
Advanced quantum state manipulation and entanglement simulation engine
Provides quantum mechanical modeling capabilities for the SR-AIbridge system
"""

import logging
import json
import random
import math
import cmath
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class QuantumState(Enum):
    """Quantum state types"""
    SUPERPOSITION = "superposition"
    ENTANGLED = "entangled"
    COLLAPSED = "collapsed"
    DECOHERENT = "decoherent"


class QubitState(Enum):
    """Individual qubit states"""
    ZERO = "0"
    ONE = "1"
    PLUS = "+"
    MINUS = "-"
    SUPERPOSED = "superposed"


@dataclass
class QuantumQubit:
    """Quantum qubit data structure"""
    qubit_id: str
    state: QubitState
    amplitude_0: complex  # Amplitude for |0⟩ state
    amplitude_1: complex  # Amplitude for |1⟩ state
    phase: float
    entangled_with: List[str]
    measurement_history: List[Tuple[datetime, str]]
    created_at: datetime
    last_updated: datetime

    def probability_0(self) -> float:
        """Calculate probability of measuring |0⟩"""
        return abs(self.amplitude_0) ** 2

    def probability_1(self) -> float:
        """Calculate probability of measuring |1⟩"""
        return abs(self.amplitude_1) ** 2

    def is_normalized(self) -> bool:
        """Check if qubit amplitudes are normalized"""
        return abs(self.probability_0() + self.probability_1() - 1.0) < 1e-10

    def to_dict(self) -> Dict[str, Any]:
        """Convert qubit to dictionary for serialization"""
        return {
            "qubit_id": self.qubit_id,
            "state": self.state.value,
            "amplitude_0": {"real": self.amplitude_0.real, "imag": self.amplitude_0.imag},
            "amplitude_1": {"real": self.amplitude_1.real, "imag": self.amplitude_1.imag},
            "phase": self.phase,
            "entangled_with": self.entangled_with,
            "probability_0": self.probability_0(),
            "probability_1": self.probability_1(),
            "is_normalized": self.is_normalized(),
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }


@dataclass
class EntanglementResult:
    """Result of quantum entanglement operation"""
    operation_id: str
    operation_type: str
    qubits_involved: List[str]
    success: bool
    fidelity: float  # 0.0 to 1.0
    execution_time_ms: float
    quantum_state: QuantumState
    bell_state: str
    timestamp: datetime


class EntangleCore:
    """
    Quantum Mechanics Engine for quantum state manipulation and simulation
    
    The EntangleCore provides advanced quantum mechanical capabilities,
    allowing the system to create superposition states, entangle qubits,
    and collapse quantum states through measurement.
    
    Key Rituals:
    - superpose: Create quantum superposition states
    - entangle: Create quantum entanglement between qubits
    - collapse: Collapse quantum states through measurement
    """
    
    def __init__(self, max_qubits: int = 20, decoherence_rate: float = 0.01):
        """
        Initialize the EntangleCore Quantum Engine
        
        Args:
            max_qubits: Maximum number of qubits to simulate
            decoherence_rate: Rate of quantum decoherence (0.0 to 1.0)
        """
        self.max_qubits = max_qubits
        self.decoherence_rate = decoherence_rate
        self.qubits: Dict[str, QuantumQubit] = {}
        self.entanglement_pairs: Dict[str, List[str]] = {}
        self.operation_results: List[EntanglementResult] = []
        self.metrics = {
            "total_qubits": 0,
            "active_qubits": 0,
            "entangled_pairs": 0,
            "superposition_count": 0,
            "collapsed_measurements": 0,
            "average_fidelity": 0.0,
            "last_operation": None
        }
        
        logger.info("⚛️ EntangleCore Quantum Engine initialized")

    def superpose(self, qubit_id: str = None, 
                 alpha: complex = None, beta: complex = None,
                 basis: str = "computational") -> QuantumQubit:
        """
        Create quantum superposition state for a qubit
        
        Args:
            qubit_id: ID for the qubit (auto-generated if None)
            alpha: Amplitude for |0⟩ state
            beta: Amplitude for |1⟩ state  
            basis: Quantum basis ("computational", "hadamard", "diagonal")
            
        Returns:
            QuantumQubit: The qubit in superposition state
        """
        start_time = datetime.now(timezone.utc)
        
        if qubit_id is None:
            qubit_id = f"q_{int(start_time.timestamp() * 1000)}"
        
        if len(self.qubits) >= self.max_qubits:
            raise ValueError(f"Maximum qubit limit reached: {self.max_qubits}")
        
        # Set default superposition amplitudes based on basis
        if alpha is None or beta is None:
            if basis == "computational":
                # Equal superposition |+⟩ = (|0⟩ + |1⟩)/√2
                alpha = complex(1/math.sqrt(2), 0)
                beta = complex(1/math.sqrt(2), 0)
            elif basis == "hadamard":
                # Hadamard basis
                alpha = complex(1/math.sqrt(2), 0)
                beta = complex(1/math.sqrt(2), 0)
            elif basis == "diagonal":
                # Diagonal basis with phase
                alpha = complex(1/math.sqrt(2), 0)
                beta = complex(0, 1/math.sqrt(2))  # i/√2
            else:
                raise ValueError(f"Unknown basis: {basis}")
        
        # Normalize amplitudes
        norm = math.sqrt(abs(alpha)**2 + abs(beta)**2)
        if norm == 0:
            raise ValueError("Cannot create qubit with zero amplitudes")
        
        alpha = alpha / norm
        beta = beta / norm
        
        # Create qubit in superposition
        qubit = QuantumQubit(
            qubit_id=qubit_id,
            state=QubitState.SUPERPOSED,
            amplitude_0=alpha,
            amplitude_1=beta,
            phase=cmath.phase(beta) - cmath.phase(alpha),
            entangled_with=[],
            measurement_history=[],
            created_at=start_time,
            last_updated=start_time
        )
        
        # Store qubit
        self.qubits[qubit_id] = qubit
        
        # Update metrics
        self.metrics["total_qubits"] += 1
        self.metrics["active_qubits"] = len([q for q in self.qubits.values() 
                                          if q.state != QubitState.ZERO and q.state != QubitState.ONE])
        self.metrics["superposition_count"] += 1
        self.metrics["last_operation"] = start_time
        
        logger.info(f"🌀 Created superposition: {qubit_id} (|0⟩: {abs(alpha):.3f}, |1⟩: {abs(beta):.3f})")
        return qubit

    def entangle(self, qubit1_id: str, qubit2_id: str, 
                bell_state: str = "phi_plus") -> EntanglementResult:
        """
        Create quantum entanglement between two qubits
        
        Args:
            qubit1_id: ID of first qubit to entangle
            qubit2_id: ID of second qubit to entangle
            bell_state: Bell state to create ("phi_plus", "phi_minus", "psi_plus", "psi_minus")
            
        Returns:
            EntanglementResult: Results of the entanglement operation
        """
        start_time = datetime.now(timezone.utc)
        operation_id = f"entangle_{int(start_time.timestamp() * 1000)}"
        
        # Validate qubits exist
        if qubit1_id not in self.qubits:
            raise ValueError(f"Qubit {qubit1_id} not found")
        if qubit2_id not in self.qubits:
            raise ValueError(f"Qubit {qubit2_id} not found")
        
        qubit1 = self.qubits[qubit1_id]
        qubit2 = self.qubits[qubit2_id]
        
        try:
            # Define Bell states
            bell_states = {
                "phi_plus": (1/math.sqrt(2), 0, 0, 1/math.sqrt(2)),      # (|00⟩ + |11⟩)/√2
                "phi_minus": (1/math.sqrt(2), 0, 0, -1/math.sqrt(2)),    # (|00⟩ - |11⟩)/√2
                "psi_plus": (0, 1/math.sqrt(2), 1/math.sqrt(2), 0),      # (|01⟩ + |10⟩)/√2
                "psi_minus": (0, 1/math.sqrt(2), -1/math.sqrt(2), 0)     # (|01⟩ - |10⟩)/√2
            }
            
            if bell_state not in bell_states:
                raise ValueError(f"Unknown Bell state: {bell_state}")
            
            # Get Bell state amplitudes
            c00, c01, c10, c11 = bell_states[bell_state]
            
            # Update qubit amplitudes for entangled state
            # This is a simplified representation - in reality, entangled states 
            # cannot be factorized into individual qubit states
            if bell_state == "phi_plus":
                # Both qubits have equal superposition with correlation
                qubit1.amplitude_0 = complex(1/math.sqrt(2), 0)
                qubit1.amplitude_1 = complex(1/math.sqrt(2), 0)
                qubit2.amplitude_0 = complex(1/math.sqrt(2), 0) 
                qubit2.amplitude_1 = complex(1/math.sqrt(2), 0)
            elif bell_state == "phi_minus":
                # Anti-correlated superposition
                qubit1.amplitude_0 = complex(1/math.sqrt(2), 0)
                qubit1.amplitude_1 = complex(1/math.sqrt(2), 0)
                qubit2.amplitude_0 = complex(1/math.sqrt(2), 0)
                qubit2.amplitude_1 = complex(-1/math.sqrt(2), 0)
            elif bell_state == "psi_plus":
                # Cross-correlated superposition
                qubit1.amplitude_0 = complex(1/math.sqrt(2), 0)
                qubit1.amplitude_1 = complex(1/math.sqrt(2), 0)
                qubit2.amplitude_0 = complex(1/math.sqrt(2), 0)
                qubit2.amplitude_1 = complex(1/math.sqrt(2), 0)
            elif bell_state == "psi_minus":
                # Anti cross-correlated superposition
                qubit1.amplitude_0 = complex(1/math.sqrt(2), 0)
                qubit1.amplitude_1 = complex(1/math.sqrt(2), 0)
                qubit2.amplitude_0 = complex(1/math.sqrt(2), 0)
                qubit2.amplitude_1 = complex(-1/math.sqrt(2), 0)
            
            # Update entanglement information
            qubit1.entangled_with.append(qubit2_id)
            qubit2.entangled_with.append(qubit1_id)
            qubit1.state = QubitState.SUPERPOSED
            qubit2.state = QubitState.SUPERPOSED
            qubit1.last_updated = start_time
            qubit2.last_updated = start_time
            
            # Store entanglement pair
            pair_key = f"{min(qubit1_id, qubit2_id)}_{max(qubit1_id, qubit2_id)}"
            self.entanglement_pairs[pair_key] = [qubit1_id, qubit2_id]
            
            # Calculate fidelity (simplified - assumes perfect entanglement)
            fidelity = self._calculate_entanglement_fidelity(qubit1, qubit2, bell_state)
            
            # Calculate execution time
            end_time = datetime.now(timezone.utc)
            execution_time = (end_time - start_time).total_seconds() * 1000
            
            # Create result
            result = EntanglementResult(
                operation_id=operation_id,
                operation_type="entangle",
                qubits_involved=[qubit1_id, qubit2_id],
                success=True,
                fidelity=fidelity,
                execution_time_ms=execution_time,
                quantum_state=QuantumState.ENTANGLED,
                bell_state=bell_state,
                timestamp=end_time
            )
            
            self.operation_results.append(result)
            
            # Update metrics
            self.metrics["entangled_pairs"] += 1
            self._update_fidelity_metrics(fidelity)
            
            logger.info(f"🔗 Entangled qubits: {qubit1_id} ↔ {qubit2_id} ({bell_state})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Entanglement failed: {str(e)}")
            
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            return EntanglementResult(
                operation_id=operation_id,
                operation_type="entangle",
                qubits_involved=[qubit1_id, qubit2_id],
                success=False,
                fidelity=0.0,
                execution_time_ms=execution_time,
                quantum_state=QuantumState.DECOHERENT,
                bell_state="none",
                timestamp=datetime.now(timezone.utc)
            )

    def collapse(self, qubit_id: str, 
                measurement_basis: str = "computational") -> EntanglementResult:
        """
        Collapse quantum state through measurement
        
        Args:
            qubit_id: ID of qubit to measure/collapse
            measurement_basis: Basis for measurement ("computational", "diagonal", "circular")
            
        Returns:
            EntanglementResult: Results of the collapse/measurement
        """
        start_time = datetime.now(timezone.utc)
        operation_id = f"collapse_{int(start_time.timestamp() * 1000)}"
        
        if qubit_id not in self.qubits:
            raise ValueError(f"Qubit {qubit_id} not found")
        
        qubit = self.qubits[qubit_id]
        
        try:
            # Store pre-measurement state
            pre_measurement_state = {
                "amplitude_0": qubit.amplitude_0,
                "amplitude_1": qubit.amplitude_1,
                "state": qubit.state
            }
            
            # Calculate measurement probabilities
            prob_0 = qubit.probability_0()
            prob_1 = qubit.probability_1()
            
            # Perform quantum measurement (probabilistic collapse)
            measurement_result = self._perform_measurement(prob_0, prob_1, measurement_basis)
            
            # Collapse the qubit state
            if measurement_result == "0":
                qubit.amplitude_0 = complex(1, 0)
                qubit.amplitude_1 = complex(0, 0)
                qubit.state = QubitState.ZERO
                measured_value = "0"
            else:
                qubit.amplitude_0 = complex(0, 0)
                qubit.amplitude_1 = complex(1, 0)
                qubit.state = QubitState.ONE
                measured_value = "1"
            
            # Handle entangled qubits - they must collapse consistently
            entangled_qubits = []
            if qubit.entangled_with:
                entangled_qubits = self._collapse_entangled_qubits(qubit_id, measured_value)
            
            # Record measurement in history
            qubit.measurement_history.append((start_time, measured_value))
            qubit.last_updated = start_time
            
            # Calculate execution time
            end_time = datetime.now(timezone.utc)
            execution_time = (end_time - start_time).total_seconds() * 1000
            
            # Calculate measurement fidelity
            fidelity = self._calculate_measurement_fidelity(pre_measurement_state, measured_value)
            
            # Create result
            result = EntanglementResult(
                operation_id=operation_id,
                operation_type="collapse",
                qubits_involved=[qubit_id] + entangled_qubits,
                success=True,
                fidelity=fidelity,
                execution_time_ms=execution_time,
                quantum_state=QuantumState.COLLAPSED,
                bell_state=f"measured_{measured_value}",
                timestamp=end_time
            )
            
            self.operation_results.append(result)
            
            # Update metrics
            self.metrics["collapsed_measurements"] += 1
            self.metrics["active_qubits"] = len([q for q in self.qubits.values() 
                                              if q.state not in [QubitState.ZERO, QubitState.ONE]])
            self._update_fidelity_metrics(fidelity)
            
            logger.info(f"📏 Collapsed qubit {qubit_id} → |{measured_value}⟩ "
                       f"(prob: {prob_0 if measured_value == '0' else prob_1:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Collapse failed for {qubit_id}: {str(e)}")
            
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            return EntanglementResult(
                operation_id=operation_id,
                operation_type="collapse",
                qubits_involved=[qubit_id],
                success=False,
                fidelity=0.0,
                execution_time_ms=execution_time,
                quantum_state=QuantumState.DECOHERENT,
                bell_state="error",
                timestamp=datetime.now(timezone.utc)
            )

    def get_qubit(self, qubit_id: str) -> Optional[QuantumQubit]:
        """Get a specific qubit by ID"""
        return self.qubits.get(qubit_id)

    def list_qubits(self, state: QubitState = None, 
                   entangled_only: bool = False) -> List[QuantumQubit]:
        """List qubits with optional filtering"""
        qubits = list(self.qubits.values())
        
        if state:
            qubits = [q for q in qubits if q.state == state]
        
        if entangled_only:
            qubits = [q for q in qubits if q.entangled_with]
        
        return qubits

    def get_entanglement_pairs(self) -> Dict[str, List[str]]:
        """Get all entanglement pairs"""
        return self.entanglement_pairs.copy()

    def get_system_state(self) -> Dict[str, Any]:
        """Get overall quantum system state"""
        total_qubits = len(self.qubits)
        superposed_qubits = len([q for q in self.qubits.values() 
                               if q.state == QubitState.SUPERPOSED])
        entangled_qubits = len([q for q in self.qubits.values() if q.entangled_with])
        
        return {
            "total_qubits": total_qubits,
            "superposed_qubits": superposed_qubits,
            "entangled_qubits": entangled_qubits,
            "entanglement_pairs": len(self.entanglement_pairs),
            "decoherence_rate": self.decoherence_rate,
            "system_entropy": self._calculate_system_entropy(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get current engine metrics"""
        return {
            **self.metrics,
            "current_qubits": len(self.qubits),
            "operation_count": len(self.operation_results),
            "system_coherence": 1.0 - self.decoherence_rate
        }

    def _perform_measurement(self, prob_0: float, prob_1: float, basis: str) -> str:
        """Perform quantum measurement with probabilistic outcome"""
        # Apply decoherence effects
        effective_prob_0 = prob_0 * (1 - self.decoherence_rate) + 0.5 * self.decoherence_rate
        effective_prob_1 = prob_1 * (1 - self.decoherence_rate) + 0.5 * self.decoherence_rate
        
        # Normalize probabilities
        total_prob = effective_prob_0 + effective_prob_1
        effective_prob_0 /= total_prob
        effective_prob_1 /= total_prob
        
        # Random measurement outcome
        random_value = random.random()
        
        if random_value < effective_prob_0:
            return "0"
        else:
            return "1"

    def _collapse_entangled_qubits(self, measured_qubit_id: str, measured_value: str) -> List[str]:
        """Collapse entangled qubits based on measurement result"""
        measured_qubit = self.qubits[measured_qubit_id]
        collapsed_qubits = []
        
        for entangled_id in measured_qubit.entangled_with:
            if entangled_id in self.qubits:
                entangled_qubit = self.qubits[entangled_id]
                
                # Determine correlated measurement result
                # This is simplified - actual entanglement collapse depends on Bell state
                if measured_value == "0":
                    # For phi_plus Bell state, correlated measurement
                    entangled_result = "0"
                else:
                    entangled_result = "1"
                
                # Collapse the entangled qubit
                if entangled_result == "0":
                    entangled_qubit.amplitude_0 = complex(1, 0)
                    entangled_qubit.amplitude_1 = complex(0, 0)
                    entangled_qubit.state = QubitState.ZERO
                else:
                    entangled_qubit.amplitude_0 = complex(0, 0)
                    entangled_qubit.amplitude_1 = complex(1, 0)
                    entangled_qubit.state = QubitState.ONE
                
                entangled_qubit.measurement_history.append((datetime.now(timezone.utc), entangled_result))
                entangled_qubit.last_updated = datetime.now(timezone.utc)
                
                collapsed_qubits.append(entangled_id)
        
        return collapsed_qubits

    def _calculate_entanglement_fidelity(self, qubit1: QuantumQubit, qubit2: QuantumQubit, 
                                       bell_state: str) -> float:
        """Calculate fidelity of entanglement operation"""
        # Simplified fidelity calculation
        # In reality, this would involve computing overlap with ideal Bell state
        
        base_fidelity = 0.95  # Assume high-fidelity operations
        
        # Reduce fidelity based on decoherence
        decoherence_penalty = self.decoherence_rate * 0.5
        fidelity = base_fidelity - decoherence_penalty
        
        # Check if qubits are properly normalized
        if not (qubit1.is_normalized() and qubit2.is_normalized()):
            fidelity *= 0.8
        
        return max(0.0, min(1.0, fidelity))

    def _calculate_measurement_fidelity(self, pre_state: Dict[str, Any], result: str) -> float:
        """Calculate fidelity of measurement operation"""
        # Calculate how likely this measurement result was
        if result == "0":
            expected_prob = abs(pre_state["amplitude_0"]) ** 2
        else:
            expected_prob = abs(pre_state["amplitude_1"]) ** 2
        
        # Fidelity based on measurement probability
        fidelity = expected_prob * (1 - self.decoherence_rate) + 0.5 * self.decoherence_rate
        
        return max(0.0, min(1.0, fidelity))

    def _calculate_system_entropy(self) -> float:
        """Calculate quantum system entropy"""
        total_entropy = 0.0
        
        for qubit in self.qubits.values():
            if qubit.state == QubitState.SUPERPOSED:
                # Von Neumann entropy for mixed state
                p0 = qubit.probability_0()
                p1 = qubit.probability_1()
                
                entropy = 0.0
                if p0 > 0:
                    entropy -= p0 * math.log2(p0)
                if p1 > 0:
                    entropy -= p1 * math.log2(p1)
                
                total_entropy += entropy
        
        return total_entropy

    def _update_fidelity_metrics(self, fidelity: float):
        """Update average fidelity metrics"""
        current_avg = self.metrics["average_fidelity"]
        operation_count = len(self.operation_results)
        
        if operation_count == 1:
            self.metrics["average_fidelity"] = fidelity
        else:
            # Running average
            self.metrics["average_fidelity"] = (
                (current_avg * (operation_count - 1) + fidelity) / operation_count
            )