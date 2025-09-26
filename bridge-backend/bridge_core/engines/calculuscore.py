"""
CalculusCore - Advanced Mathematical Engine
Calculus and advanced mathematical computation engine
Extends ProofFoundry with specialized calculus capabilities
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import sympy as sp
from sympy import symbols, diff, integrate, limit, series, solve, oo

from ..prooffoundry import ProofFoundry

logger = logging.getLogger(__name__)


class CalculusCore(ProofFoundry):
    """
    Advanced Mathematical Engine extending ProofFoundry
    
    The CalculusCore provides specialized calculus capabilities,
    allowing the system to perform differentiation, integration,
    limits, series analysis, and advanced mathematical modeling.
    
    Key Rituals:
    - differentiate: Compute symbolic derivatives
    - integrate: Compute symbolic integrals
    - limit_analysis: Analyze function limits
    - series_expand: Generate series expansions
    - optimize: Find function extrema
    """
    
    def __init__(self, precision: int = 15, timeout_seconds: int = 30, max_terms: int = 10):
        super().__init__(precision=precision, timeout_seconds=timeout_seconds)
        self.max_terms = max_terms
        self.calculus_results: Dict[str, Dict[str, Any]] = {}
        logger.info("∫ CalculusCore Engine initialized")
    
    def differentiate(self, equation_id: str, variable: str, 
                     order: int = 1, at_point: Optional[float] = None) -> Dict[str, Any]:
        """
        Compute symbolic derivatives
        
        Args:
            equation_id: ID of equation to differentiate
            variable: Variable to differentiate with respect to
            order: Order of derivative (1st, 2nd, etc.)
            at_point: Optional point to evaluate derivative at
            
        Returns:
            Dict containing derivative results
        """
        start_time = datetime.utcnow()
        
        if equation_id not in self.equations:
            return {"error": f"Equation {equation_id} not found"}
        
        equation = self.equations[equation_id]
        
        try:
            # Get the symbolic expression
            expr = equation.symbolic_form
            var = symbols(variable)
            
            # Compute derivative
            derivative = diff(expr, var, order)
            
            # Evaluate at point if specified
            evaluated = None
            if at_point is not None:
                try:
                    evaluated = float(derivative.subs(var, at_point))
                except (ValueError, TypeError):
                    evaluated = "Could not evaluate numerically"
            
            result = {
                "equation_id": equation_id,
                "operation": "differentiate",
                "variable": variable,
                "order": order,
                "derivative": str(derivative),
                "derivative_latex": sp.latex(derivative),
                "simplified": str(sp.simplify(derivative)),
                "at_point": at_point,
                "evaluated": evaluated,
                "computed_at": start_time.isoformat(),
                "success": True
            }
            
            # Store result
            result_id = f"diff_{equation_id}_{variable}_{order}_{int(start_time.timestamp() * 1000)}"
            self.calculus_results[result_id] = result
            
            logger.info(f"∂ Computed {order}-order derivative of {equation_id} with respect to {variable}")
            
            return result
            
        except Exception as e:
            error_result = {
                "equation_id": equation_id,
                "operation": "differentiate", 
                "error": str(e),
                "success": False,
                "computed_at": start_time.isoformat()
            }
            logger.error(f"❌ Differentiation failed for {equation_id}: {e}")
            return error_result
    
    def integrate(self, equation_id: str, variable: str,
                 limits: Optional[Tuple[float, float]] = None,
                 method: str = "symbolic") -> Dict[str, Any]:
        """
        Compute symbolic or definite integrals
        
        Args:
            equation_id: ID of equation to integrate
            variable: Variable to integrate with respect to
            limits: Optional integration limits (a, b) for definite integral
            method: Integration method (symbolic, numerical)
            
        Returns:
            Dict containing integration results
        """
        start_time = datetime.utcnow()
        
        if equation_id not in self.equations:
            return {"error": f"Equation {equation_id} not found"}
        
        equation = self.equations[equation_id]
        
        try:
            # Get the symbolic expression
            expr = equation.symbolic_form
            var = symbols(variable)
            
            # Compute integral
            if limits is None:
                # Indefinite integral
                integral = integrate(expr, var)
                integral_type = "indefinite"
            else:
                # Definite integral
                integral = integrate(expr, (var, limits[0], limits[1]))
                integral_type = "definite"
            
            # Try to evaluate numerically if it's a definite integral
            numerical_value = None
            if limits is not None:
                try:
                    numerical_value = float(integral)
                except (ValueError, TypeError):
                    numerical_value = "Could not evaluate numerically"
            
            result = {
                "equation_id": equation_id,
                "operation": "integrate",
                "variable": variable,
                "limits": limits,
                "integral_type": integral_type,
                "integral": str(integral),
                "integral_latex": sp.latex(integral),
                "simplified": str(sp.simplify(integral)),
                "numerical_value": numerical_value,
                "method": method,
                "computed_at": start_time.isoformat(),
                "success": True
            }
            
            # Store result
            result_id = f"int_{equation_id}_{variable}_{int(start_time.timestamp() * 1000)}"
            self.calculus_results[result_id] = result
            
            logger.info(f"∫ Computed {integral_type} integral of {equation_id} with respect to {variable}")
            
            return result
            
        except Exception as e:
            error_result = {
                "equation_id": equation_id,
                "operation": "integrate",
                "error": str(e),
                "success": False,
                "computed_at": start_time.isoformat()
            }
            logger.error(f"❌ Integration failed for {equation_id}: {e}")
            return error_result
    
    def limit_analysis(self, equation_id: str, variable: str,
                      approach_point: str, direction: str = "both") -> Dict[str, Any]:
        """
        Analyze function limits
        
        Args:
            equation_id: ID of equation to analyze
            variable: Variable in the limit
            approach_point: Point to approach (number, 'oo', '-oo')
            direction: Direction of approach ('both', 'left', 'right')
            
        Returns:
            Dict containing limit analysis results
        """
        start_time = datetime.utcnow()
        
        if equation_id not in self.equations:
            return {"error": f"Equation {equation_id} not found"}
        
        equation = self.equations[equation_id]
        
        try:
            # Get the symbolic expression
            expr = equation.symbolic_form
            var = symbols(variable)
            
            # Parse approach point
            if approach_point == "oo":
                point = oo
            elif approach_point == "-oo":
                point = -oo
            else:
                point = float(approach_point)
            
            # Compute limits based on direction
            limits_computed = {}
            
            if direction in ["both", "left"]:
                try:
                    left_limit = limit(expr, var, point, '-')
                    limits_computed["left"] = str(left_limit)
                except:
                    limits_computed["left"] = "undefined"
            
            if direction in ["both", "right"]:
                try:
                    right_limit = limit(expr, var, point, '+')
                    limits_computed["right"] = str(right_limit)
                except:
                    limits_computed["right"] = "undefined"
            
            if direction == "both":
                try:
                    two_sided_limit = limit(expr, var, point)
                    limits_computed["two_sided"] = str(two_sided_limit)
                except:
                    limits_computed["two_sided"] = "undefined"
            
            # Determine if limit exists
            limit_exists = False
            if direction == "both":
                limit_exists = (limits_computed.get("left") == limits_computed.get("right") 
                              and limits_computed.get("left") != "undefined")
            else:
                limit_exists = any(v != "undefined" for v in limits_computed.values())
            
            result = {
                "equation_id": equation_id,
                "operation": "limit_analysis",
                "variable": variable,
                "approach_point": approach_point,
                "direction": direction,
                "limits": limits_computed,
                "limit_exists": limit_exists,
                "computed_at": start_time.isoformat(),
                "success": True
            }
            
            # Store result
            result_id = f"lim_{equation_id}_{variable}_{approach_point}_{int(start_time.timestamp() * 1000)}"
            self.calculus_results[result_id] = result
            
            logger.info(f"lim Analyzed limit of {equation_id} as {variable} → {approach_point}")
            
            return result
            
        except Exception as e:
            error_result = {
                "equation_id": equation_id,
                "operation": "limit_analysis",
                "error": str(e),
                "success": False,
                "computed_at": start_time.isoformat()
            }
            logger.error(f"❌ Limit analysis failed for {equation_id}: {e}")
            return error_result
    
    def series_expand(self, equation_id: str, variable: str,
                     center: float = 0, order: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate series expansions (Taylor, Maclaurin, etc.)
        
        Args:
            equation_id: ID of equation to expand
            variable: Variable for expansion
            center: Center point for expansion
            order: Number of terms (uses self.max_terms if None)
            
        Returns:
            Dict containing series expansion results
        """
        start_time = datetime.utcnow()
        
        if equation_id not in self.equations:
            return {"error": f"Equation {equation_id} not found"}
        
        equation = self.equations[equation_id]
        expansion_order = order if order is not None else self.max_terms
        
        try:
            # Get the symbolic expression
            expr = equation.symbolic_form
            var = symbols(variable)
            
            # Compute series expansion
            series_expansion = series(expr, var, center, expansion_order).removeO()
            
            # Extract coefficients
            coefficients = []
            for i in range(expansion_order):
                try:
                    coeff = series_expansion.coeff(var, i)
                    if coeff is not None:
                        coefficients.append({"power": i, "coefficient": str(coeff)})
                except:
                    continue
            
            result = {
                "equation_id": equation_id,
                "operation": "series_expand",
                "variable": variable,
                "center": center,
                "order": expansion_order,
                "series": str(series_expansion),
                "series_latex": sp.latex(series_expansion),
                "coefficients": coefficients,
                "series_type": "Taylor" if center != 0 else "Maclaurin",
                "computed_at": start_time.isoformat(),
                "success": True
            }
            
            # Store result
            result_id = f"series_{equation_id}_{variable}_{center}_{int(start_time.timestamp() * 1000)}"
            self.calculus_results[result_id] = result
            
            logger.info(f"∑ Computed series expansion of {equation_id} around {variable} = {center}")
            
            return result
            
        except Exception as e:
            error_result = {
                "equation_id": equation_id,
                "operation": "series_expand",
                "error": str(e),
                "success": False,
                "computed_at": start_time.isoformat()
            }
            logger.error(f"❌ Series expansion failed for {equation_id}: {e}")
            return error_result
    
    def optimize(self, equation_id: str, variable: str,
                optimization_type: str = "critical_points") -> Dict[str, Any]:
        """
        Find function extrema and critical points
        
        Args:
            equation_id: ID of equation to optimize
            variable: Variable to optimize over
            optimization_type: Type of optimization (critical_points, minima, maxima)
            
        Returns:
            Dict containing optimization results
        """
        start_time = datetime.utcnow()
        
        if equation_id not in self.equations:
            return {"error": f"Equation {equation_id} not found"}
        
        equation = self.equations[equation_id]
        
        try:
            # Get the symbolic expression
            expr = equation.symbolic_form
            var = symbols(variable)
            
            # Compute first derivative
            first_derivative = diff(expr, var)
            
            # Find critical points (where derivative = 0)
            critical_points = solve(first_derivative, var)
            
            # Compute second derivative for classification
            second_derivative = diff(first_derivative, var)
            
            # Classify critical points
            classified_points = []
            for point in critical_points:
                try:
                    second_deriv_value = second_derivative.subs(var, point)
                    
                    if second_deriv_value > 0:
                        point_type = "local_minimum"
                    elif second_deriv_value < 0:
                        point_type = "local_maximum"
                    else:
                        point_type = "inflection_point"
                    
                    function_value = expr.subs(var, point)
                    
                    classified_points.append({
                        "point": str(point),
                        "type": point_type,
                        "function_value": str(function_value),
                        "second_derivative": str(second_deriv_value)
                    })
                except:
                    classified_points.append({
                        "point": str(point),
                        "type": "undetermined",
                        "function_value": "undefined",
                        "second_derivative": "undefined"
                    })
            
            result = {
                "equation_id": equation_id,
                "operation": "optimize",
                "variable": variable,
                "optimization_type": optimization_type,
                "first_derivative": str(first_derivative),
                "second_derivative": str(second_derivative),
                "critical_points": classified_points,
                "critical_point_count": len(classified_points),
                "computed_at": start_time.isoformat(),
                "success": True
            }
            
            # Store result
            result_id = f"opt_{equation_id}_{variable}_{int(start_time.timestamp() * 1000)}"
            self.calculus_results[result_id] = result
            
            logger.info(f"📈 Found {len(classified_points)} critical points for {equation_id}")
            
            return result
            
        except Exception as e:
            error_result = {
                "equation_id": equation_id,
                "operation": "optimize",
                "error": str(e),
                "success": False,
                "computed_at": start_time.isoformat()
            }
            logger.error(f"❌ Optimization failed for {equation_id}: {e}")
            return error_result
    
    def get_calculus_results(self, operation_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get calculus computation results"""
        if operation_type:
            return [r for r in self.calculus_results.values() if r.get("operation") == operation_type]
        return list(self.calculus_results.values())
    
    def get_calculus_metrics(self) -> Dict[str, Any]:
        """Get CalculusCore-specific metrics"""
        base_metrics = self.get_metrics()
        
        operation_counts = {}
        for result in self.calculus_results.values():
            op = result.get("operation", "unknown")
            operation_counts[op] = operation_counts.get(op, 0) + 1
        
        return {
            **base_metrics,
            "calculus_operations": len(self.calculus_results),
            "max_terms": self.max_terms,
            "operation_breakdown": operation_counts,
            "successful_operations": sum(1 for r in self.calculus_results.values() if r.get("success", False))
        }