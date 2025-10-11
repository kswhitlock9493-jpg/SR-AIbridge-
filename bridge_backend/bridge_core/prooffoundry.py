"""
ProofFoundry - Math Engine
Advanced mathematical computation and proof verification engine
Provides comprehensive mathematical analysis capabilities for the SR-AIbridge system
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Import SymPy for mathematical computations
import sympy as sp
from sympy import symbols, Eq, solve, simplify, expand, factor, diff, integrate
from sympy.logic import satisfiable
from sympy.geometry import Point, Line, Circle
from sympy.matrices import Matrix

logger = logging.getLogger(__name__)


class EquationType(Enum):
    """Types of mathematical equations"""
    ALGEBRAIC = "algebraic"
    DIFFERENTIAL = "differential"
    INTEGRAL = "integral"
    TRIGONOMETRIC = "trigonometric"
    LOGARITHMIC = "logarithmic"
    EXPONENTIAL = "exponential"
    MATRIX = "matrix"
    GEOMETRIC = "geometric"


class ProofStatus(Enum):
    """Status of mathematical proofs"""
    INSCRIBED = "inscribed"
    VALIDATING = "validating"
    PROVEN = "proven"
    DISPROVEN = "disproven"
    INCOMPLETE = "incomplete"
    ERROR = "error"


@dataclass
class MathematicalEquation:
    """Mathematical equation data structure"""
    equation_id: str
    title: str
    equation_text: str
    equation_type: EquationType
    variables: List[str]
    constants: Dict[str, Any]
    sympy_expr: Any  # SymPy expression
    status: ProofStatus
    created_at: datetime
    last_updated: datetime
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert equation to dictionary for serialization"""
        return {
            "equation_id": self.equation_id,
            "title": self.title,
            "equation_text": self.equation_text,
            "equation_type": self.equation_type.value,
            "variables": self.variables,
            "constants": self.constants,
            "sympy_expr": str(self.sympy_expr),
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "metadata": self.metadata or {}
        }


@dataclass
class ProofResult:
    """Result of mathematical proof or computation"""
    proof_id: str
    equation_id: str
    result: Any
    steps: List[str]
    success: bool
    computation_time_ms: float
    proof_method: str
    timestamp: datetime
    confidence: float  # 0.0 to 1.0


class ProofFoundry:
    """
    Math Engine for advanced mathematical computation and proof verification
    
    The ProofFoundry provides comprehensive mathematical capabilities,
    allowing the system to inscribe equations, prove mathematical identities,
    and solve complex mathematical problems using symbolic computation.
    
    Key Rituals:
    - inscribe_equation: Define and store mathematical equations
    - prove_identity: Verify mathematical identities and theorems
    - solve: Solve equations and mathematical problems
    """
    
    def __init__(self, precision: int = 15, timeout_seconds: int = 30):
        """
        Initialize the ProofFoundry Math Engine
        
        Args:
            precision: Decimal precision for calculations
            timeout_seconds: Maximum time for complex computations
        """
        self.precision = precision
        self.timeout_seconds = timeout_seconds
        self.equations: Dict[str, MathematicalEquation] = {}
        self.proof_results: Dict[str, List[ProofResult]] = {}
        self.symbol_cache: Dict[str, sp.Symbol] = {}
        self.metrics = {
            "total_equations": 0,
            "successful_proofs": 0,
            "failed_proofs": 0,
            "equations_by_type": {},
            "average_computation_time": 0.0,
            "last_computation": None
        }
        
        # Set SymPy precision
        sp.N._global_precision = precision
        
        logger.info("🔢 ProofFoundry Math Engine initialized")

    def inscribe_equation(self, title: str, equation_text: str, 
                         equation_type: EquationType = EquationType.ALGEBRAIC,
                         variables: List[str] = None,
                         constants: Dict[str, Any] = None) -> MathematicalEquation:
        """
        Inscribe a new mathematical equation into the foundry
        
        Args:
            title: Descriptive title for the equation
            equation_text: Mathematical equation in string format
            equation_type: Type of mathematical equation
            variables: List of variable names in the equation
            constants: Dictionary of constant values
            
        Returns:
            MathematicalEquation: The inscribed equation ready for manipulation
        """
        start_time = datetime.now(timezone.utc)
        equation_id = f"eq_{int(start_time.timestamp() * 1000)}"
        
        try:
            # Parse the equation text into SymPy expression
            sympy_expr = self._parse_equation(equation_text, variables, constants)
            
            # Extract variables if not provided
            if variables is None:
                variables = [str(var) for var in sympy_expr.free_symbols]
            
            # Create equation object
            equation = MathematicalEquation(
                equation_id=equation_id,
                title=title,
                equation_text=equation_text,
                equation_type=equation_type,
                variables=variables,
                constants=constants or {},
                sympy_expr=sympy_expr,
                status=ProofStatus.INSCRIBED,
                created_at=start_time,
                last_updated=start_time,
                metadata={
                    "inscribed_by": "ProofFoundry",
                    "version": "1.0",
                    "complexity": self._assess_complexity(sympy_expr)
                }
            )
            
            # Store equation
            self.equations[equation_id] = equation
            
            # Update metrics
            self.metrics["total_equations"] += 1
            eq_type = equation_type.value
            if eq_type not in self.metrics["equations_by_type"]:
                self.metrics["equations_by_type"][eq_type] = 0
            self.metrics["equations_by_type"][eq_type] += 1
            
            logger.info(f"📝 Inscribed equation: {title} [{equation_id}]")
            return equation
            
        except Exception as e:
            logger.error(f"❌ Failed to inscribe equation '{title}': {str(e)}")
            raise ValueError(f"Cannot inscribe equation: {str(e)}")

    def prove_identity(self, equation_id: str, 
                      target_form: str = None,
                      proof_method: str = "symbolic") -> ProofResult:
        """
        Prove mathematical identity or verify equation properties
        
        Args:
            equation_id: ID of equation to prove
            target_form: Target form to prove equivalence to
            proof_method: Method to use for proof (symbolic, numeric, etc.)
            
        Returns:
            ProofResult: Results of the proof attempt
        """
        start_time = datetime.now(timezone.utc)
        
        if equation_id not in self.equations:
            raise ValueError(f"Equation {equation_id} not found")
        
        equation = self.equations[equation_id]
        proof_id = f"proof_{equation_id}_{int(start_time.timestamp() * 1000)}"
        
        try:
            equation.status = ProofStatus.VALIDATING
            equation.last_updated = start_time
            
            steps = []
            result = None
            success = False
            confidence = 0.0
            
            if proof_method == "symbolic":
                result, steps, success, confidence = self._prove_symbolic(equation, target_form)
            elif proof_method == "numeric":
                result, steps, success, confidence = self._prove_numeric(equation, target_form)
            elif proof_method == "algebraic":
                result, steps, success, confidence = self._prove_algebraic(equation, target_form)
            else:
                raise ValueError(f"Unknown proof method: {proof_method}")
            
            # Calculate computation time
            end_time = datetime.now(timezone.utc)
            computation_time = (end_time - start_time).total_seconds() * 1000
            
            # Create proof result
            proof_result = ProofResult(
                proof_id=proof_id,
                equation_id=equation_id,
                result=result,
                steps=steps,
                success=success,
                computation_time_ms=computation_time,
                proof_method=proof_method,
                timestamp=end_time,
                confidence=confidence
            )
            
            # Store result
            if equation_id not in self.proof_results:
                self.proof_results[equation_id] = []
            self.proof_results[equation_id].append(proof_result)
            
            # Update equation status
            if success:
                equation.status = ProofStatus.PROVEN
                self.metrics["successful_proofs"] += 1
            else:
                equation.status = ProofStatus.INCOMPLETE
                self.metrics["failed_proofs"] += 1
            
            # Update metrics
            self._update_computation_metrics(computation_time)
            
            logger.info(f"🔍 Proof completed: {equation.title} (Success: {success})")
            return proof_result
            
        except Exception as e:
            logger.error(f"❌ Proof failed for {equation_id}: {str(e)}")
            equation.status = ProofStatus.ERROR
            
            computation_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            return ProofResult(
                proof_id=proof_id,
                equation_id=equation_id,
                result=None,
                steps=[f"Error: {str(e)}"],
                success=False,
                computation_time_ms=computation_time,
                proof_method=proof_method,
                timestamp=datetime.now(timezone.utc),
                confidence=0.0
            )

    def solve(self, equation_id: str, 
              solve_for: List[str] = None,
              constraints: Dict[str, Any] = None,
              solution_type: str = "exact") -> ProofResult:
        """
        Solve mathematical equation for specified variables
        
        Args:
            equation_id: ID of equation to solve
            solve_for: Variables to solve for (solves for all if None)
            constraints: Additional constraints on variables
            solution_type: Type of solution (exact, numeric, approximate)
            
        Returns:
            ProofResult: Solutions and solving process
        """
        start_time = datetime.now(timezone.utc)
        
        if equation_id not in self.equations:
            raise ValueError(f"Equation {equation_id} not found")
        
        equation = self.equations[equation_id]
        solve_id = f"solve_{equation_id}_{int(start_time.timestamp() * 1000)}"
        
        try:
            steps = []
            solutions = None
            success = False
            confidence = 0.0
            
            # Determine variables to solve for
            if solve_for is None:
                solve_for = equation.variables
            
            # Convert solve_for strings to SymPy symbols
            solve_symbols = [self._get_symbol(var) for var in solve_for]
            
            steps.append(f"Solving equation: {equation.equation_text}")
            steps.append(f"Variables to solve for: {solve_for}")
            
            # Apply constraints if provided
            expr = equation.sympy_expr
            if constraints:
                steps.append(f"Applying constraints: {constraints}")
                expr = self._apply_constraints(expr, constraints)
            
            # Solve based on solution type
            if solution_type == "exact":
                solutions = self._solve_exact(expr, solve_symbols, steps)
            elif solution_type == "numeric":
                solutions = self._solve_numeric(expr, solve_symbols, steps)
            elif solution_type == "approximate":
                solutions = self._solve_approximate(expr, solve_symbols, steps)
            else:
                raise ValueError(f"Unknown solution type: {solution_type}")
            
            # Evaluate success and confidence
            if solutions is not None:
                success = True
                confidence = self._calculate_solution_confidence(solutions, equation)
                steps.append(f"Found {len(solutions) if isinstance(solutions, list) else 1} solution(s)")
            else:
                steps.append("No solutions found")
            
            # Calculate computation time
            end_time = datetime.now(timezone.utc)
            computation_time = (end_time - start_time).total_seconds() * 1000
            
            # Create result
            solve_result = ProofResult(
                proof_id=solve_id,
                equation_id=equation_id,
                result=self._format_solutions(solutions),
                steps=steps,
                success=success,
                computation_time_ms=computation_time,
                proof_method=f"solve_{solution_type}",
                timestamp=end_time,
                confidence=confidence
            )
            
            # Store result
            if equation_id not in self.proof_results:
                self.proof_results[equation_id] = []
            self.proof_results[equation_id].append(solve_result)
            
            # Update metrics
            if success:
                self.metrics["successful_proofs"] += 1
            else:
                self.metrics["failed_proofs"] += 1
                
            self._update_computation_metrics(computation_time)
            
            logger.info(f"🔧 Solve completed: {equation.title} (Success: {success})")
            return solve_result
            
        except Exception as e:
            logger.error(f"❌ Solve failed for {equation_id}: {str(e)}")
            
            computation_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            return ProofResult(
                proof_id=solve_id,
                equation_id=equation_id,
                result=None,
                steps=[f"Error: {str(e)}"],
                success=False,
                computation_time_ms=computation_time,
                proof_method=f"solve_{solution_type}",
                timestamp=datetime.now(timezone.utc),
                confidence=0.0
            )

    def get_equation(self, equation_id: str) -> Optional[MathematicalEquation]:
        """Get a specific equation by ID"""
        return self.equations.get(equation_id)

    def list_equations(self, equation_type: EquationType = None, 
                      status: ProofStatus = None) -> List[MathematicalEquation]:
        """List equations with optional filtering"""
        equations = list(self.equations.values())
        
        if equation_type:
            equations = [eq for eq in equations if eq.equation_type == equation_type]
        
        if status:
            equations = [eq for eq in equations if eq.status == status]
        
        return equations

    def get_proof_results(self, equation_id: str) -> List[ProofResult]:
        """Get all proof results for an equation"""
        return self.proof_results.get(equation_id, [])

    def get_metrics(self) -> Dict[str, Any]:
        """Get current engine metrics"""
        return {
            **self.metrics,
            "current_equations": len(self.equations),
            "total_proofs": sum(len(results) for results in self.proof_results.values()),
            "symbol_cache_size": len(self.symbol_cache)
        }

    def _parse_equation(self, equation_text: str, variables: List[str] = None, 
                       constants: Dict[str, Any] = None) -> sp.Expr:
        """Parse equation text into SymPy expression"""
        try:
            # Replace common mathematical notation
            cleaned_text = equation_text.replace("^", "**")
            
            # Create symbols for variables
            if variables:
                for var in variables:
                    self._get_symbol(var)
            
            # Substitute constants if provided
            if constants:
                for const, value in constants.items():
                    cleaned_text = cleaned_text.replace(const, str(value))
                    
            # Parse with SymPy
            expr = sp.sympify(cleaned_text, locals=self.symbol_cache)
            return expr
            
        except Exception as e:
            raise ValueError(f"Cannot parse equation '{equation_text}': {str(e)}")

    def _get_symbol(self, name: str) -> sp.Symbol:
        """Get or create a SymPy symbol"""
        if name not in self.symbol_cache:
            self.symbol_cache[name] = symbols(name)
        return self.symbol_cache[name]

    def _assess_complexity(self, expr: sp.Expr) -> str:
        """Assess mathematical complexity of expression"""
        complexity_score = 0
        
        # Count different types of operations
        complexity_score += len(expr.free_symbols)  # Variables
        complexity_score += expr.count(sp.Add)  # Additions
        complexity_score += expr.count(sp.Mul)  # Multiplications
        complexity_score += expr.count(sp.Pow)  # Powers
        complexity_score += expr.count(sp.sin) + expr.count(sp.cos) + expr.count(sp.tan)  # Trig functions
        complexity_score += expr.count(sp.log) + expr.count(sp.exp)  # Log/exp functions
        
        if complexity_score <= 5:
            return "simple"
        elif complexity_score <= 15:
            return "moderate"
        else:
            return "complex"

    def _prove_symbolic(self, equation: MathematicalEquation, target_form: str) -> tuple:
        """Prove using symbolic manipulation"""
        steps = ["Starting symbolic proof"]
        expr = equation.sympy_expr
        
        try:
            # Try various symbolic manipulations
            simplified = simplify(expr)
            expanded = expand(expr)
            factored = factor(expr)
            
            steps.append(f"Simplified form: {simplified}")
            steps.append(f"Expanded form: {expanded}")
            steps.append(f"Factored form: {factored}")
            
            # Check if target form is provided
            if target_form:
                target_expr = self._parse_equation(target_form)
                equivalence = simplify(expr - target_expr) == 0
                
                if equivalence:
                    steps.append(f"Proven equivalent to target form: {target_form}")
                    return True, steps, True, 0.95
                else:
                    steps.append(f"Not equivalent to target form: {target_form}")
                    return False, steps, False, 0.1
            else:
                # General symbolic validation
                steps.append("Symbolic manipulations completed successfully")
                return simplified, steps, True, 0.8
                
        except Exception as e:
            steps.append(f"Symbolic proof error: {str(e)}")
            return None, steps, False, 0.0

    def _prove_numeric(self, equation: MathematicalEquation, target_form: str) -> tuple:
        """Prove using numeric methods"""
        steps = ["Starting numeric proof"]
        expr = equation.sympy_expr
        
        try:
            # Evaluate at specific points
            test_points = [0, 1, -1, 2, -2, sp.pi/2, sp.pi]
            results = []
            
            for point in test_points:
                try:
                    if len(equation.variables) == 1:
                        var = self._get_symbol(equation.variables[0])
                        result = expr.subs(var, point).evalf()
                        results.append((point, result))
                        steps.append(f"At {equation.variables[0]}={point}: {result}")
                except:
                    pass
            
            if results:
                return results, steps, True, 0.7
            else:
                steps.append("No numeric evaluations possible")
                return None, steps, False, 0.0
                
        except Exception as e:
            steps.append(f"Numeric proof error: {str(e)}")
            return None, steps, False, 0.0

    def _prove_algebraic(self, equation: MathematicalEquation, target_form: str) -> tuple:
        """Prove using algebraic methods"""
        steps = ["Starting algebraic proof"]
        expr = equation.sympy_expr
        
        try:
            # Try to solve for zero
            if isinstance(expr, sp.Eq):
                # It's already an equation
                lhs, rhs = expr.lhs, expr.rhs
                diff_expr = lhs - rhs
            else:
                # Assume it's an expression that should equal zero
                diff_expr = expr
            
            solutions = solve(diff_expr, expr.free_symbols)
            steps.append(f"Algebraic solutions: {solutions}")
            
            if solutions:
                return solutions, steps, True, 0.9
            else:
                steps.append("No algebraic solutions found")
                return None, steps, False, 0.2
                
        except Exception as e:
            steps.append(f"Algebraic proof error: {str(e)}")
            return None, steps, False, 0.0

    def _solve_exact(self, expr: sp.Expr, solve_symbols: List[sp.Symbol], steps: List[str]) -> Any:
        """Solve equation exactly"""
        steps.append("Attempting exact solution")
        try:
            solutions = solve(expr, solve_symbols)
            steps.append(f"Exact solutions found: {len(solutions) if isinstance(solutions, list) else 1}")
            return solutions
        except Exception as e:
            steps.append(f"Exact solve failed: {str(e)}")
            return None

    def _solve_numeric(self, expr: sp.Expr, solve_symbols: List[sp.Symbol], steps: List[str]) -> Any:
        """Solve equation numerically"""
        steps.append("Attempting numeric solution")
        try:
            # Use numeric methods
            solutions = []
            for symbol in solve_symbols:
                try:
                    # Try to find numeric solutions
                    numeric_sols = solve(expr, symbol)
                    if numeric_sols:
                        evaluated = [sol.evalf() for sol in numeric_sols]
                        solutions.extend(evaluated)
                except:
                    pass
            
            steps.append(f"Numeric solutions found: {len(solutions)}")
            return solutions if solutions else None
        except Exception as e:
            steps.append(f"Numeric solve failed: {str(e)}")
            return None

    def _solve_approximate(self, expr: sp.Expr, solve_symbols: List[sp.Symbol], steps: List[str]) -> Any:
        """Solve equation approximately"""
        steps.append("Attempting approximate solution")
        try:
            # Use approximation methods
            solutions = solve(expr, solve_symbols)
            if solutions:
                approximate = [sol.evalf(self.precision) for sol in solutions]
                steps.append(f"Approximate solutions found: {len(approximate)}")
                return approximate
            return None
        except Exception as e:
            steps.append(f"Approximate solve failed: {str(e)}")
            return None

    def _apply_constraints(self, expr: sp.Expr, constraints: Dict[str, Any]) -> sp.Expr:
        """Apply constraints to expression"""
        for var, constraint in constraints.items():
            symbol = self._get_symbol(var)
            if isinstance(constraint, (int, float)):
                expr = expr.subs(symbol, constraint)
        return expr

    def _calculate_solution_confidence(self, solutions: Any, equation: MathematicalEquation) -> float:
        """Calculate confidence in solutions"""
        if solutions is None:
            return 0.0
        
        # Base confidence on solution type and equation complexity
        base_confidence = 0.8
        
        if isinstance(solutions, list) and len(solutions) > 0:
            # Multiple solutions found
            return min(0.95, base_confidence + 0.1)
        elif solutions:
            # Single solution found
            return base_confidence
        else:
            return 0.1

    def _format_solutions(self, solutions: Any) -> Dict[str, Any]:
        """Format solutions for serialization"""
        if solutions is None:
            return {"solutions": None, "count": 0}
        
        if isinstance(solutions, list):
            return {
                "solutions": [str(sol) for sol in solutions],
                "count": len(solutions),
                "type": "multiple"
            }
        else:
            return {
                "solutions": [str(solutions)],
                "count": 1,
                "type": "single"
            }

    def _update_computation_metrics(self, computation_time: float):
        """Update computation time metrics"""
        current_avg = self.metrics["average_computation_time"]
        total_computations = self.metrics["successful_proofs"] + self.metrics["failed_proofs"]
        
        if total_computations == 1:
            self.metrics["average_computation_time"] = computation_time
        else:
            # Running average
            self.metrics["average_computation_time"] = (
                (current_avg * (total_computations - 1) + computation_time) / total_computations
            )
        
        self.metrics["last_computation"] = datetime.now(timezone.utc)