"""
LabyrinthForge - Science Engine
Advanced scientific hypothesis testing and experimental validation engine
Provides methodical scientific exploration capabilities for the SR-AIbridge system
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ExperimentStatus(Enum):
    """Status of scientific experiments"""
    PROPOSED = "proposed"
    TESTING = "testing"
    VALIDATED = "validated"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


class HypothesisType(Enum):
    """Types of scientific hypotheses"""
    OBSERVATIONAL = "observational"
    EXPERIMENTAL = "experimental"
    THEORETICAL = "theoretical"
    COMPUTATIONAL = "computational"


@dataclass
class ScientificHypothesis:
    """Scientific hypothesis data structure"""
    hypothesis_id: str
    title: str
    description: str
    hypothesis_type: HypothesisType
    variables: Dict[str, Any]
    expected_outcome: str
    confidence: float  # 0.0 to 1.0
    status: ExperimentStatus
    created_at: datetime
    last_updated: datetime
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert hypothesis to dictionary for serialization"""
        return {
            "hypothesis_id": self.hypothesis_id,
            "title": self.title,
            "description": self.description,
            "hypothesis_type": self.hypothesis_type.value,
            "variables": self.variables,
            "expected_outcome": self.expected_outcome,
            "confidence": self.confidence,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "metadata": self.metadata or {}
        }


@dataclass
class ExperimentResult:
    """Result of scientific experiment"""
    experiment_id: str
    hypothesis_id: str
    result_data: Dict[str, Any]
    success: bool
    confidence_score: float
    observations: List[str]
    execution_time_ms: float
    timestamp: datetime


class LabyrinthForge:
    """
    Science Engine for hypothesis testing and experimental validation
    
    The LabyrinthForge provides advanced scientific exploration capabilities,
    allowing the system to propose hypotheses, conduct virtual experiments,
    and validate results through rigorous testing methodologies.
    
    Key Rituals:
    - propose: Generate and structure scientific hypotheses
    - test: Execute controlled experiments and collect data
    - validate: Analyze results and determine hypothesis validity
    """
    
    def __init__(self, max_concurrent_experiments: int = 10):
        """
        Initialize the LabyrinthForge Science Engine
        
        Args:
            max_concurrent_experiments: Maximum number of experiments to run simultaneously
        """
        self.max_concurrent_experiments = max_concurrent_experiments
        self.hypotheses: Dict[str, ScientificHypothesis] = {}
        self.experiment_results: Dict[str, List[ExperimentResult]] = {}
        self.active_experiments: Dict[str, datetime] = {}
        self.metrics = {
            "total_hypotheses": 0,
            "successful_experiments": 0,
            "failed_experiments": 0,
            "average_confidence": 0.0,
            "last_experiment": None
        }
        logger.info("🧪 LabyrinthForge Science Engine initialized")

    def propose(self, title: str, description: str, 
                hypothesis_type: HypothesisType = HypothesisType.EXPERIMENTAL,
                variables: Dict[str, Any] = None, 
                expected_outcome: str = "",
                initial_confidence: float = 0.5) -> ScientificHypothesis:
        """
        Propose a new scientific hypothesis for investigation
        
        Args:
            title: Clear, concise hypothesis title
            description: Detailed hypothesis description
            hypothesis_type: Type of scientific hypothesis
            variables: Variables and parameters to test
            expected_outcome: Expected result or behavior
            initial_confidence: Initial confidence level (0.0-1.0)
            
        Returns:
            ScientificHypothesis: The proposed hypothesis ready for testing
        """
        start_time = datetime.utcnow()
        hypothesis_id = f"hyp_{int(start_time.timestamp() * 1000)}"
        
        hypothesis = ScientificHypothesis(
            hypothesis_id=hypothesis_id,
            title=title,
            description=description,
            hypothesis_type=hypothesis_type,
            variables=variables or {},
            expected_outcome=expected_outcome,
            confidence=max(0.0, min(1.0, initial_confidence)),
            status=ExperimentStatus.PROPOSED,
            created_at=start_time,
            last_updated=start_time,
            metadata={"proposed_by": "LabyrinthForge", "version": "1.0"}
        )
        
        self.hypotheses[hypothesis_id] = hypothesis
        self.metrics["total_hypotheses"] += 1
        
        logger.info(f"🔬 Proposed hypothesis: {title} [{hypothesis_id}]")
        return hypothesis

    def test(self, hypothesis_id: str, test_parameters: Dict[str, Any] = None) -> ExperimentResult:
        """
        Execute controlled testing of a scientific hypothesis
        
        Args:
            hypothesis_id: ID of hypothesis to test
            test_parameters: Additional parameters for the experiment
            
        Returns:
            ExperimentResult: Results of the experimental testing
        """
        start_time = datetime.utcnow()
        
        if hypothesis_id not in self.hypotheses:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")
        
        hypothesis = self.hypotheses[hypothesis_id]
        
        # Check concurrent experiment limits
        if len(self.active_experiments) >= self.max_concurrent_experiments:
            logger.warning("⚠️ Maximum concurrent experiments reached")
            
        # Mark experiment as active
        experiment_id = f"exp_{hypothesis_id}_{int(start_time.timestamp() * 1000)}"
        self.active_experiments[experiment_id] = start_time
        
        # Update hypothesis status
        hypothesis.status = ExperimentStatus.TESTING
        hypothesis.last_updated = start_time
        
        try:
            # Simulate experimental testing with the provided variables and parameters
            test_params = test_parameters or {}
            variables = {**hypothesis.variables, **test_params}
            
            # Execute virtual experiment based on hypothesis type
            result_data = self._execute_experiment(hypothesis, variables)
            
            # Analyze results
            success = self._analyze_results(hypothesis, result_data)
            confidence_score = self._calculate_confidence(hypothesis, result_data, success)
            
            # Generate observations
            observations = self._generate_observations(hypothesis, result_data, success)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            result = ExperimentResult(
                experiment_id=experiment_id,
                hypothesis_id=hypothesis_id,
                result_data=result_data,
                success=success,
                confidence_score=confidence_score,
                observations=observations,
                execution_time_ms=execution_time,
                timestamp=datetime.utcnow()
            )
            
            # Store results
            if hypothesis_id not in self.experiment_results:
                self.experiment_results[hypothesis_id] = []
            self.experiment_results[hypothesis_id].append(result)
            
            # Update metrics
            if success:
                self.metrics["successful_experiments"] += 1
                hypothesis.status = ExperimentStatus.VALIDATED
            else:
                self.metrics["failed_experiments"] += 1
                hypothesis.status = ExperimentStatus.FAILED
                
            self.metrics["last_experiment"] = datetime.utcnow()
            self._update_average_confidence()
            
            logger.info(f"🧪 Experiment completed: {experiment_id} (Success: {success})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Experiment failed: {experiment_id} - {str(e)}")
            hypothesis.status = ExperimentStatus.FAILED
            raise
        finally:
            # Remove from active experiments
            if experiment_id in self.active_experiments:
                del self.active_experiments[experiment_id]

    def validate(self, hypothesis_id: str, validation_criteria: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate hypothesis results against scientific criteria
        
        Args:
            hypothesis_id: ID of hypothesis to validate
            validation_criteria: Specific criteria for validation
            
        Returns:
            Dict containing validation results and recommendations
        """
        if hypothesis_id not in self.hypotheses:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")
        
        hypothesis = self.hypotheses[hypothesis_id]
        results = self.experiment_results.get(hypothesis_id, [])
        
        if not results:
            return {
                "valid": False,
                "reason": "No experimental results available",
                "recommendations": ["Run test() method first to generate experimental data"]
            }
        
        # Apply validation criteria
        criteria = validation_criteria or {
            "min_confidence": 0.7,
            "min_experiments": 1,
            "require_success": True
        }
        
        # Analyze all results for this hypothesis
        successful_experiments = [r for r in results if r.success]
        average_confidence = sum(r.confidence_score for r in results) / len(results)
        
        validation_result = {
            "hypothesis_id": hypothesis_id,
            "hypothesis_title": hypothesis.title,
            "total_experiments": len(results),
            "successful_experiments": len(successful_experiments),
            "average_confidence": average_confidence,
            "valid": False,
            "confidence_level": "low",
            "recommendations": []
        }
        
        # Check validation criteria
        if len(results) >= criteria.get("min_experiments", 1):
            if criteria.get("require_success", True) and successful_experiments:
                if average_confidence >= criteria.get("min_confidence", 0.7):
                    validation_result["valid"] = True
                    validation_result["confidence_level"] = "high" if average_confidence >= 0.9 else "medium"
                    hypothesis.status = ExperimentStatus.VALIDATED
                else:
                    validation_result["recommendations"].append(f"Confidence too low: {average_confidence:.2f} < {criteria['min_confidence']}")
            else:
                validation_result["recommendations"].append("No successful experiments found")
        else:
            validation_result["recommendations"].append(f"Need more experiments: {len(results)} < {criteria['min_experiments']}")
        
        if not validation_result["valid"]:
            validation_result["recommendations"].append("Consider refining hypothesis or experimental parameters")
            hypothesis.status = ExperimentStatus.INCONCLUSIVE
        
        logger.info(f"🔍 Validation completed for {hypothesis_id}: {validation_result['valid']}")
        return validation_result

    def get_hypothesis(self, hypothesis_id: str) -> Optional[ScientificHypothesis]:
        """Get a specific hypothesis by ID"""
        return self.hypotheses.get(hypothesis_id)

    def list_hypotheses(self, status: ExperimentStatus = None) -> List[ScientificHypothesis]:
        """List all hypotheses, optionally filtered by status"""
        if status:
            return [h for h in self.hypotheses.values() if h.status == status]
        return list(self.hypotheses.values())

    def get_metrics(self) -> Dict[str, Any]:
        """Get current engine metrics and statistics"""
        return {
            **self.metrics,
            "active_experiments": len(self.active_experiments),
            "total_results": sum(len(results) for results in self.experiment_results.values())
        }

    def _execute_experiment(self, hypothesis: ScientificHypothesis, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute virtual experiment based on hypothesis parameters"""
        # Simulate experimental execution
        result_data = {
            "variables_tested": variables,
            "measurements": {},
            "conditions": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Generate synthetic measurements based on hypothesis type
        if hypothesis.hypothesis_type == HypothesisType.EXPERIMENTAL:
            result_data["measurements"] = {"value": sum(v for v in variables.values() if isinstance(v, (int, float)))}
        elif hypothesis.hypothesis_type == HypothesisType.OBSERVATIONAL:
            result_data["observations"] = [f"Observed behavior with {k}={v}" for k, v in variables.items()]
        elif hypothesis.hypothesis_type == HypothesisType.THEORETICAL:
            result_data["theoretical_validation"] = {"consistency": True, "predictions": ["prediction_1", "prediction_2"]}
        elif hypothesis.hypothesis_type == HypothesisType.COMPUTATIONAL:
            result_data["computation_results"] = {"iterations": 1000, "convergence": True}
        
        return result_data

    def _analyze_results(self, hypothesis: ScientificHypothesis, result_data: Dict[str, Any]) -> bool:
        """Analyze experimental results to determine success"""
        # Simple success criteria based on hypothesis type
        if hypothesis.hypothesis_type == HypothesisType.EXPERIMENTAL:
            return "measurements" in result_data and result_data["measurements"]
        elif hypothesis.hypothesis_type == HypothesisType.THEORETICAL:
            return result_data.get("theoretical_validation", {}).get("consistency", False)
        elif hypothesis.hypothesis_type == HypothesisType.COMPUTATIONAL:
            return result_data.get("computation_results", {}).get("convergence", False)
        else:
            return True  # Observational studies are generally successful if data is collected

    def _calculate_confidence(self, hypothesis: ScientificHypothesis, result_data: Dict[str, Any], success: bool) -> float:
        """Calculate confidence score based on results"""
        base_confidence = hypothesis.confidence
        
        if success:
            # Increase confidence for successful experiments
            confidence_boost = 0.2
            return min(1.0, base_confidence + confidence_boost)
        else:
            # Decrease confidence for failed experiments
            confidence_penalty = 0.3
            return max(0.0, base_confidence - confidence_penalty)

    def _generate_observations(self, hypothesis: ScientificHypothesis, result_data: Dict[str, Any], success: bool) -> List[str]:
        """Generate scientific observations from experimental results"""
        observations = []
        
        if success:
            observations.append(f"Hypothesis '{hypothesis.title}' showed positive results")
            observations.append("Experimental conditions were within acceptable parameters")
        else:
            observations.append(f"Hypothesis '{hypothesis.title}' did not meet expected outcomes")
            observations.append("Consider revising experimental approach or parameters")
        
        # Add specific observations based on result data
        if "measurements" in result_data:
            observations.append(f"Measurements recorded: {len(result_data['measurements'])} data points")
        
        if "variables_tested" in result_data:
            observations.append(f"Variables tested: {list(result_data['variables_tested'].keys())}")
        
        return observations

    def _update_average_confidence(self):
        """Update running average confidence metric"""
        if not self.experiment_results:
            return
        
        all_results = [result for results in self.experiment_results.values() for result in results]
        if all_results:
            self.metrics["average_confidence"] = sum(r.confidence_score for r in all_results) / len(all_results)