"""
QHelmSingularity - Quantum Helm Engine
Advanced quantum navigation and singularity physics engine
Extends EntangleCore with quantum helm and spacetime navigation
"""

import logging
import math
import cmath
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..entanglecore import EntangleCore, QuantumState, QubitState

logger = logging.getLogger(__name__)


class SingularityType(Enum):
    """Types of spacetime singularities"""
    BLACK_HOLE = "black_hole"
    WHITE_HOLE = "white_hole"
    WORMHOLE = "wormhole"
    NAKED_SINGULARITY = "naked_singularity"
    QUANTUM_FOAM = "quantum_foam"


class NavigationMode(Enum):
    """Quantum navigation modes"""
    CLASSICAL = "classical"
    QUANTUM_TUNNELING = "quantum_tunneling"
    ENTANGLEMENT_BRIDGE = "entanglement_bridge"
    SPACETIME_FOLD = "spacetime_fold"
    PROBABILITY_PATH = "probability_path"


@dataclass
class SingularityPoint:
    """Spacetime singularity data structure"""
    singularity_id: str
    singularity_type: SingularityType
    coordinates: Tuple[float, float, float, float]  # x, y, z, t
    mass_energy: float
    event_horizon: float
    quantum_signature: complex
    stability_index: float
    created_at: str


@dataclass
class QuantumRoute:
    """Quantum navigation route"""
    route_id: str
    origin: Tuple[float, float, float, float]
    destination: Tuple[float, float, float, float]
    navigation_mode: NavigationMode
    waypoints: List[Tuple[float, float, float, float]]
    probability_amplitude: complex
    entanglement_cost: float
    traversal_time: float
    success_probability: float
    created_at: str


class QHelmSingularity(EntangleCore):
    """
    Quantum Helm Engine extending EntangleCore
    
    The QHelmSingularity provides advanced quantum navigation and
    spacetime manipulation capabilities, allowing the system to
    navigate through quantum fields and manipulate singularities.
    
    Key Rituals:
    - navigate: Plot quantum navigation routes
    - manifest_singularity: Create spacetime singularities
    - fold_spacetime: Manipulate spacetime geometry
    - helm_control: Direct quantum navigation
    """
    
    def __init__(self, max_qubits: int = 20, decoherence_rate: float = 0.01, 
                 max_singularities: int = 10):
        super().__init__(max_qubits=max_qubits, decoherence_rate=decoherence_rate)
        self.max_singularities = max_singularities
        self.singularities: Dict[str, SingularityPoint] = {}
        self.quantum_routes: Dict[str, QuantumRoute] = {}
        self.helm_position: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
        self.navigation_history: List[Dict[str, Any]] = []
        logger.info("🚀 QHelmSingularity Engine initialized")
    
    def navigate(self, destination: Tuple[float, float, float, float],
                navigation_mode: NavigationMode = NavigationMode.QUANTUM_TUNNELING,
                max_waypoints: int = 5) -> Dict[str, Any]:
        """
        Plot quantum navigation routes through spacetime
        
        Args:
            destination: Target coordinates (x, y, z, t)
            navigation_mode: Method of quantum navigation
            max_waypoints: Maximum number of waypoint calculations
            
        Returns:
            Dict containing navigation route and analysis
        """
        start_time = datetime.now(timezone.utc)
        
        if len(self.quantum_routes) >= 100:  # Prevent memory overflow
            # Remove oldest routes
            oldest_routes = sorted(self.quantum_routes.items(), 
                                 key=lambda x: x[1].created_at)[:10]
            for route_id, _ in oldest_routes:
                del self.quantum_routes[route_id]
        
        route_id = f"route_{int(start_time.timestamp() * 1000)}"
        
        # Calculate route through quantum spacetime
        waypoints = self._calculate_quantum_waypoints(
            self.helm_position, destination, navigation_mode, max_waypoints
        )
        
        # Calculate probability amplitude for successful navigation
        probability_amplitude = self._calculate_route_amplitude(
            self.helm_position, destination, waypoints, navigation_mode
        )
        
        # Calculate entanglement cost and traversal time
        entanglement_cost = self._calculate_entanglement_cost(waypoints, navigation_mode)
        traversal_time = self._calculate_traversal_time(waypoints, navigation_mode)
        success_probability = abs(probability_amplitude) ** 2
        
        # Create quantum route
        quantum_route = QuantumRoute(
            route_id=route_id,
            origin=self.helm_position,
            destination=destination,
            navigation_mode=navigation_mode,
            waypoints=waypoints,
            probability_amplitude=probability_amplitude,
            entanglement_cost=entanglement_cost,
            traversal_time=traversal_time,
            success_probability=success_probability,
            created_at=start_time.isoformat()
        )
        
        self.quantum_routes[route_id] = quantum_route
        
        logger.info(f"🧭 Plotted quantum route to {destination} with {len(waypoints)} waypoints")
        
        return {
            "route_id": route_id,
            "origin": self.helm_position,
            "destination": destination,
            "navigation_mode": navigation_mode.value,
            "waypoints": waypoints,
            "waypoint_count": len(waypoints),
            "probability_amplitude_real": probability_amplitude.real,
            "probability_amplitude_imag": probability_amplitude.imag,
            "entanglement_cost": entanglement_cost,
            "traversal_time": traversal_time,
            "success_probability": success_probability,
            "created_at": start_time.isoformat(),
            "navigation_feasible": success_probability > 0.1
        }
    
    def manifest_singularity(self, coordinates: Tuple[float, float, float, float],
                           singularity_type: SingularityType,
                           mass_energy: float) -> Dict[str, Any]:
        """
        Create spacetime singularities for navigation
        
        Args:
            coordinates: Spacetime coordinates for singularity
            singularity_type: Type of singularity to manifest
            mass_energy: Mass-energy of the singularity
            
        Returns:
            Dict containing manifested singularity data
        """
        start_time = datetime.now(timezone.utc)
        
        if len(self.singularities) >= self.max_singularities:
            logger.warning("⚠️ Maximum singularities reached")
            return {"error": "Singularity limit exceeded"}
        
        singularity_id = f"sing_{singularity_type.value}_{int(start_time.timestamp() * 1000)}"
        
        # Calculate singularity properties
        event_horizon = self._calculate_event_horizon(mass_energy, singularity_type)
        quantum_signature = self._generate_quantum_signature(coordinates, mass_energy)
        stability_index = self._calculate_stability_index(mass_energy, singularity_type)
        
        # Create singularity point
        singularity = SingularityPoint(
            singularity_id=singularity_id,
            singularity_type=singularity_type,
            coordinates=coordinates,
            mass_energy=mass_energy,
            event_horizon=event_horizon,
            quantum_signature=quantum_signature,
            stability_index=stability_index,
            created_at=start_time.isoformat()
        )
        
        self.singularities[singularity_id] = singularity
        
        # Record in navigation history
        self.navigation_history.append({
            "action": "manifest_singularity",
            "singularity_id": singularity_id,
            "coordinates": coordinates,
            "singularity_type": singularity_type.value,
            "timestamp": start_time.isoformat()
        })
        
        logger.info(f"🕳️ Manifested {singularity_type.value} singularity at {coordinates}")
        
        return {
            "singularity_id": singularity_id,
            "singularity_type": singularity_type.value,
            "coordinates": coordinates,
            "mass_energy": mass_energy,
            "event_horizon": event_horizon,
            "quantum_signature_real": quantum_signature.real,
            "quantum_signature_imag": quantum_signature.imag,
            "stability_index": stability_index,
            "stable": stability_index > 0.5,
            "created_at": start_time.isoformat()
        }
    
    def fold_spacetime(self, fold_origin: Tuple[float, float, float, float],
                      fold_destination: Tuple[float, float, float, float],
                      fold_strength: float = 1.0) -> Dict[str, Any]:
        """
        Manipulate spacetime geometry for faster travel
        
        Args:
            fold_origin: Origin point of spacetime fold
            fold_destination: Destination point of spacetime fold
            fold_strength: Strength of the spacetime fold (0.0-1.0)
            
        Returns:
            Dict containing spacetime fold results
        """
        start_time = datetime.now(timezone.utc)
        
        # Calculate fold parameters
        fold_distance = self._calculate_spacetime_distance(fold_origin, fold_destination)
        energy_required = fold_distance * fold_strength * 100  # Arbitrary energy scaling
        
        # Check if we have enough quantum resources
        available_qubits = len([q for q in self.qubits.values() 
                              if q.state != QubitState.COLLAPSED])
        
        if available_qubits < energy_required / 10:
            return {
                "error": "Insufficient quantum resources for spacetime fold",
                "energy_required": energy_required,
                "available_qubits": available_qubits
            }
        
        # Calculate fold efficiency and side effects
        fold_efficiency = min(fold_strength * available_qubits / (energy_required / 10), 1.0)
        temporal_distortion = fold_strength * 0.1  # Time dilation effect
        
        # Create spacetime fold
        fold_result = {
            "fold_id": f"fold_{int(start_time.timestamp() * 1000)}",
            "fold_origin": fold_origin,
            "fold_destination": fold_destination,
            "fold_strength": fold_strength,
            "fold_distance": fold_distance,
            "energy_required": energy_required,
            "energy_consumed": energy_required * fold_efficiency,
            "fold_efficiency": fold_efficiency,
            "temporal_distortion": temporal_distortion,
            "travel_time_reduction": fold_efficiency * 0.8,  # Up to 80% reduction
            "side_effects": self._calculate_fold_side_effects(fold_strength),
            "created_at": start_time.isoformat(),
            "success": fold_efficiency > 0.3
        }
        
        # Consume quantum resources
        qubits_to_consume = int(energy_required * fold_efficiency / 10)
        consumed_qubits = []
        
        for qubit_id, qubit in list(self.qubits.items()):
            if len(consumed_qubits) >= qubits_to_consume:
                break
            if qubit.state != QubitState.COLLAPSED:
                # Collapse qubit to consume its energy
                self.qubits[qubit_id].state = QubitState.COLLAPSED
                consumed_qubits.append(qubit_id)
        
        fold_result["consumed_qubits"] = consumed_qubits
        
        # Record in history
        self.navigation_history.append({
            "action": "fold_spacetime",
            "fold_id": fold_result["fold_id"],
            "efficiency": fold_efficiency,
            "timestamp": start_time.isoformat()
        })
        
        logger.info(f"🌀 Folded spacetime from {fold_origin} to {fold_destination} with {fold_efficiency:.2f} efficiency")
        
        return fold_result
    
    def helm_control(self, new_position: Tuple[float, float, float, float],
                    control_mode: str = "direct") -> Dict[str, Any]:
        """
        Direct quantum helm control for navigation
        
        Args:
            new_position: New spacetime coordinates
            control_mode: Control mode (direct, assisted, autopilot)
            
        Returns:
            Dict containing helm control results
        """
        start_time = datetime.now(timezone.utc)
        
        old_position = self.helm_position
        
        # Calculate movement vector and energy cost
        movement_distance = self._calculate_spacetime_distance(old_position, new_position)
        energy_cost = movement_distance * 0.1  # Base energy cost
        
        # Apply control mode modifiers
        if control_mode == "assisted":
            energy_cost *= 0.8  # 20% energy reduction
        elif control_mode == "autopilot":
            energy_cost *= 0.6  # 40% energy reduction
        
        # Check for nearby singularities that might affect navigation
        nearby_singularities = []
        for sing_id, singularity in self.singularities.items():
            sing_distance = self._calculate_spacetime_distance(new_position, singularity.coordinates)
            if sing_distance < singularity.event_horizon * 2:
                nearby_singularities.append({
                    "singularity_id": sing_id,
                    "distance": sing_distance,
                    "influence": singularity.event_horizon / max(sing_distance, 0.01)
                })
        
        # Update helm position
        self.helm_position = new_position
        
        # Calculate navigation accuracy based on quantum coherence
        coherence = 1.0 - self.decoherence_rate
        navigation_accuracy = coherence * (1.0 - min(energy_cost / 100, 0.5))
        
        result = {
            "helm_control_id": f"helm_{int(start_time.timestamp() * 1000)}",
            "old_position": old_position,
            "new_position": new_position,
            "control_mode": control_mode,
            "movement_distance": movement_distance,
            "energy_cost": energy_cost,
            "navigation_accuracy": navigation_accuracy,
            "nearby_singularities": nearby_singularities,
            "quantum_coherence": coherence,
            "timestamp": start_time.isoformat(),
            "success": navigation_accuracy > 0.5
        }
        
        # Record in history
        self.navigation_history.append({
            "action": "helm_control",
            "old_position": old_position,
            "new_position": new_position,
            "control_mode": control_mode,
            "timestamp": start_time.isoformat()
        })
        
        logger.info(f"🚁 Helm navigated from {old_position} to {new_position}")
        
        return result
    
    def get_singularities(self) -> List[Dict[str, Any]]:
        """Get all manifested singularities"""
        return [
            {
                "singularity_id": s.singularity_id,
                "singularity_type": s.singularity_type.value,
                "coordinates": s.coordinates,
                "mass_energy": s.mass_energy,
                "event_horizon": s.event_horizon,
                "stability_index": s.stability_index,
                "created_at": s.created_at
            }
            for s in self.singularities.values()
        ]
    
    def get_quantum_routes(self) -> List[Dict[str, Any]]:
        """Get all plotted quantum routes"""
        return [
            {
                "route_id": r.route_id,
                "origin": r.origin,
                "destination": r.destination,
                "navigation_mode": r.navigation_mode.value,
                "waypoint_count": len(r.waypoints),
                "success_probability": r.success_probability,
                "traversal_time": r.traversal_time,
                "created_at": r.created_at
            }
            for r in self.quantum_routes.values()
        ]
    
    def get_helm_metrics(self) -> Dict[str, Any]:
        """Get QHelmSingularity-specific metrics"""
        base_metrics = self.get_metrics()
        
        return {
            **base_metrics,
            "current_position": self.helm_position,
            "active_singularities": len(self.singularities),
            "max_singularities": self.max_singularities,
            "plotted_routes": len(self.quantum_routes),
            "navigation_history_length": len(self.navigation_history),
            "stable_singularities": sum(1 for s in self.singularities.values() if s.stability_index > 0.5)
        }
    
    # Private helper methods
    def _calculate_quantum_waypoints(self, origin: Tuple[float, float, float, float],
                                   destination: Tuple[float, float, float, float],
                                   mode: NavigationMode, max_waypoints: int) -> List[Tuple[float, float, float, float]]:
        """Calculate quantum navigation waypoints"""
        waypoints = []
        
        # Simple linear interpolation with quantum uncertainty
        for i in range(1, min(max_waypoints + 1, 6)):
            t = i / (max_waypoints + 1)
            
            # Add quantum uncertainty to waypoints
            uncertainty = 0.1 if mode == NavigationMode.QUANTUM_TUNNELING else 0.05
            
            waypoint = (
                origin[0] + t * (destination[0] - origin[0]) + (hash(str(i)) % 100 - 50) * uncertainty / 50,
                origin[1] + t * (destination[1] - origin[1]) + (hash(str(i + 1)) % 100 - 50) * uncertainty / 50,
                origin[2] + t * (destination[2] - origin[2]) + (hash(str(i + 2)) % 100 - 50) * uncertainty / 50,
                origin[3] + t * (destination[3] - origin[3]) + (hash(str(i + 3)) % 100 - 50) * uncertainty / 50
            )
            waypoints.append(waypoint)
        
        return waypoints
    
    def _calculate_route_amplitude(self, origin: Tuple[float, float, float, float],
                                 destination: Tuple[float, float, float, float],
                                 waypoints: List[Tuple[float, float, float, float]],
                                 mode: NavigationMode) -> complex:
        """Calculate quantum probability amplitude for route"""
        distance = self._calculate_spacetime_distance(origin, destination)
        
        # Base amplitude decreases with distance
        base_amplitude = math.exp(-distance * 0.01)
        
        # Mode-specific modifications
        if mode == NavigationMode.QUANTUM_TUNNELING:
            phase = distance * 0.1
        elif mode == NavigationMode.ENTANGLEMENT_BRIDGE:
            phase = 0  # Zero phase for entangled systems
        else:
            phase = distance * 0.05
        
        return complex(base_amplitude * math.cos(phase), base_amplitude * math.sin(phase))
    
    def _calculate_entanglement_cost(self, waypoints: List[Tuple[float, float, float, float]],
                                   mode: NavigationMode) -> float:
        """Calculate entanglement resources required"""
        base_cost = len(waypoints) * 2.0
        
        if mode == NavigationMode.ENTANGLEMENT_BRIDGE:
            return base_cost * 2.0  # Higher cost for entanglement
        elif mode == NavigationMode.QUANTUM_TUNNELING:
            return base_cost * 1.5
        else:
            return base_cost
    
    def _calculate_traversal_time(self, waypoints: List[Tuple[float, float, float, float]],
                                mode: NavigationMode) -> float:
        """Calculate time required for navigation"""
        base_time = len(waypoints) * 1.0
        
        if mode == NavigationMode.SPACETIME_FOLD:
            return base_time * 0.3  # Faster with spacetime folding
        elif mode == NavigationMode.QUANTUM_TUNNELING:
            return base_time * 0.5  # Tunneling is faster
        else:
            return base_time
    
    def _calculate_spacetime_distance(self, pos1: Tuple[float, float, float, float],
                                    pos2: Tuple[float, float, float, float]) -> float:
        """Calculate spacetime distance using Minkowski metric"""
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        dz = pos2[2] - pos1[2]
        dt = pos2[3] - pos1[3]
        
        # Minkowski spacetime metric: ds² = -c²dt² + dx² + dy² + dz²
        # Simplified with c = 1
        spacetime_interval = -dt*dt + dx*dx + dy*dy + dz*dz
        
        # Return proper distance (always positive)
        return math.sqrt(abs(spacetime_interval))
    
    def _calculate_event_horizon(self, mass_energy: float, singularity_type: SingularityType) -> float:
        """Calculate event horizon radius"""
        # Simplified Schwarzschild radius: r = 2GM/c² 
        # With G*c normalized to 1
        base_radius = 2 * mass_energy
        
        if singularity_type == SingularityType.BLACK_HOLE:
            return base_radius
        elif singularity_type == SingularityType.WHITE_HOLE:
            return base_radius * 0.8
        elif singularity_type == SingularityType.WORMHOLE:
            return base_radius * 1.5
        else:
            return base_radius * 0.5
    
    def _generate_quantum_signature(self, coordinates: Tuple[float, float, float, float],
                                  mass_energy: float) -> complex:
        """Generate unique quantum signature for singularity"""
        # Create complex signature based on coordinates and mass
        real_part = (coordinates[0] + coordinates[1]) * mass_energy * 0.01
        imag_part = (coordinates[2] + coordinates[3]) * mass_energy * 0.01
        
        return complex(real_part, imag_part)
    
    def _calculate_stability_index(self, mass_energy: float, singularity_type: SingularityType) -> float:
        """Calculate singularity stability"""
        base_stability = min(mass_energy / 100.0, 1.0)
        
        if singularity_type == SingularityType.BLACK_HOLE:
            return base_stability * 0.9
        elif singularity_type == SingularityType.WHITE_HOLE:
            return base_stability * 0.3  # Less stable
        elif singularity_type == SingularityType.WORMHOLE:
            return base_stability * 0.6
        else:
            return base_stability * 0.8
    
    def _calculate_fold_side_effects(self, fold_strength: float) -> List[str]:
        """Calculate side effects of spacetime folding"""
        effects = []
        
        if fold_strength > 0.8:
            effects.append("severe temporal distortion")
        elif fold_strength > 0.6:
            effects.append("moderate temporal distortion")
        
        if fold_strength > 0.7:
            effects.append("gravitational wave emission")
        
        if fold_strength > 0.9:
            effects.append("potential causality violation")
        
        return effects