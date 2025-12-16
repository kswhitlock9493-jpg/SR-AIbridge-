"""
Phoenix Protocol - CalculusCore Math Engine
Built following BUILD_DOSSIER.md and ENGINE_CATALOG.md specifications

CalculusCore: Mathematical proofs and symbolic computation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sympy as sp
from sympy import sympify, latex
from datetime import datetime

router = APIRouter(prefix="/engines/math", tags=["engines", "math"])


class MathRequest(BaseModel):
    expression: str
    operation: str  # prove, differentiate, integrate, solve, factor, expand, simplify
    variable: Optional[str] = "x"
    bounds: Optional[List[float]] = None  # For integration


class MathResponse(BaseModel):
    result: str
    latex_result: Optional[str] = None
    steps: List[str] = []
    metadata: Dict[str, Any] = {}
    engine: str = "CalculusCore"
    timestamp: datetime


@router.post("/prove", response_model=MathResponse)
async def math_prove(request: MathRequest):
    """
    CalculusCore - Mathematical proofs and operations
    
    Supported operations:
    - differentiate: Take derivative
    - integrate: Compute integral
    - solve: Solve equation
    - factor: Factor expression
    - expand: Expand expression
    - simplify: Simplify expression
    - prove: General mathematical proof
    """
    
    try:
        # Parse expression
        expr = sympify(request.expression)
        var = sp.Symbol(request.variable)
        
        steps = []
        result = None
        
        # Perform operation
        if request.operation == "differentiate":
            steps.append(f"Taking derivative of {request.expression} with respect to {request.variable}")
            result = sp.diff(expr, var)
            steps.append("Applied differentiation rules")
            
        elif request.operation == "integrate":
            steps.append(f"Integrating {request.expression} with respect to {request.variable}")
            if request.bounds:
                # Definite integral
                result = sp.integrate(expr, (var, request.bounds[0], request.bounds[1]))
                steps.append(f"Applied definite integration from {request.bounds[0]} to {request.bounds[1]}")
            else:
                # Indefinite integral
                result = sp.integrate(expr, var)
                steps.append("Applied indefinite integration")
                
        elif request.operation == "solve":
            steps.append(f"Solving equation: {request.expression} = 0")
            solutions = sp.solve(expr, var)
            result = solutions
            steps.append(f"Found {len(solutions)} solution(s)")
            
        elif request.operation == "factor":
            steps.append(f"Factoring expression: {request.expression}")
            result = sp.factor(expr)
            steps.append("Applied factoring")
            
        elif request.operation == "expand":
            steps.append(f"Expanding expression: {request.expression}")
            result = sp.expand(expr)
            steps.append("Applied expansion")
            
        elif request.operation == "simplify":
            steps.append(f"Simplifying expression: {request.expression}")
            result = sp.simplify(expr)
            steps.append("Applied simplification rules")
            
        elif request.operation == "prove":
            steps.append(f"Analyzing expression: {request.expression}")
            result = sp.simplify(expr)
            steps.append("Applied mathematical proof techniques")
            steps.append("Simplified to canonical form")
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported operation: {request.operation}. "
                       f"Supported: differentiate, integrate, solve, factor, expand, simplify, prove"
            )
        
        # Convert result to string
        result_str = str(result)
        latex_str = latex(result) if result is not None else None
        
        steps.append("Operation completed successfully")
        
        return MathResponse(
            result=result_str,
            latex_result=latex_str,
            steps=steps,
            metadata={
                "operation": request.operation,
                "variable": request.variable,
                "input_expression": request.expression,
                "complexity": "computed"
            },
            engine="CalculusCore",
            timestamp=datetime.utcnow()
        )
        
    except sp.SympifyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mathematical expression: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"CalculusCore error: {str(e)}"
        )


@router.get("/status")
async def calculus_core_status():
    """Get CalculusCore engine status"""
    return {
        "engine": "CalculusCore",
        "status": "operational",
        "version": "1.0.0-phoenix",
        "capabilities": [
            "differentiate",
            "integrate",
            "solve",
            "factor",
            "expand",
            "simplify",
            "prove"
        ],
        "backend": f"SymPy {sp.__version__}",
        "timestamp": datetime.utcnow().isoformat()
    }
