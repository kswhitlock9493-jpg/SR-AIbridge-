"""
Sovereign Engines API Routes
RESTful endpoints for MicroScribe, MicroLogician, and Compliance Guard
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import logging

from bridge_backend.bridge_engines.sovereign_guard import SovereignComplianceGuard, ComplianceResult
from bridge_backend.bridge_engines.micro_scribe import SovereignMicroScribe, DiffAnalysis, PRTemplate
from bridge_backend.bridge_engines.micro_logician import SovereignMicroLogician, LogAnalysis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bridge/engines", tags=["sovereign-engines"])

# Initialize engines
compliance_guard = SovereignComplianceGuard()
micro_scribe = SovereignMicroScribe()
micro_logician = SovereignMicroLogician()


@router.get("/status")
async def get_engines_status():
    """Get status of all sovereign engines"""
    # Check compliance for status operation
    compliance = compliance_guard.check_compliance("status_check")
    
    return {
        "status": "operational",
        "engines": {
            "compliance_guard": {
                "name": "Sovereign Compliance Guard",
                "version": "1.0.0",
                "operational": True,
                "features": [
                    "quantum-resistant-license",
                    "bridge-resonance-aware",
                    "military-grade-audit",
                    "sovereign-policy-enforcement"
                ]
            },
            "micro_scribe": {
                "name": "Sovereign MicroScribe Engine",
                "version": "1.0.0",
                "operational": True,
                "features": [
                    "quantum-diff-analysis",
                    "resonance-aware-pr-generation",
                    "security-validation",
                    "risk-assessment"
                ]
            },
            "micro_logician": {
                "name": "Sovereign MicroLogician Engine",
                "version": "1.0.0",
                "operational": True,
                "features": [
                    "quantum-pattern-detection",
                    "security-intelligence",
                    "performance-analytics",
                    "anomaly-detection"
                ]
            }
        },
        "compliance": {
            "status": "COMPLIANT" if compliance.compliant else "VIOLATION",
            "license_valid": compliance.license_valid,
            "resonance_sufficient": compliance.resonance_sufficient,
            "policy_enforced": compliance.policy_enforced
        }
    }


@router.get("/compliance/check")
async def check_compliance(operation: str, route: Optional[str] = None):
    """
    Check compliance for an operation
    
    Args:
        operation: Operation to validate
        route: Optional route being accessed
    """
    result = compliance_guard.check_compliance(operation, route)
    return result.model_dump()


@router.get("/compliance/audit")
async def get_audit_trail(limit: int = 100):
    """
    Get audit trail entries
    
    Args:
        limit: Maximum number of entries to return (default: 100)
    """
    # Check compliance for audit access
    if not compliance_guard.validate_operation("audit_access"):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access audit trail"
        )
    
    entries = compliance_guard.get_audit_trail(limit)
    return {
        "count": len(entries),
        "entries": entries
    }


@router.post("/microscribe/analyze")
async def analyze_diff(diff_file: UploadFile = File(...)):
    """
    Analyze a diff file with quantum-enhanced security validation
    
    Upload a git diff file for analysis
    """
    # Check compliance
    if not compliance_guard.validate_operation("diff_analysis"):
        raise HTTPException(
            status_code=403,
            detail="Diff analysis not authorized - check compliance"
        )
    
    try:
        # Read diff content
        diff_content = await diff_file.read()
        diff_text = diff_content.decode('utf-8')
        
        # Analyze diff
        analysis = micro_scribe.analyze_diff(diff_text)
        
        return analysis.model_dump()
    
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid diff file - must be UTF-8 encoded text"
        )
    except Exception as e:
        logger.error(f"Diff analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/microscribe/generate-pr")
async def generate_pr(
    diff_file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form("")
):
    """
    Generate PR template from diff analysis
    
    Args:
        diff_file: Git diff file
        title: PR title
        description: Optional PR description
    """
    # Check compliance
    if not compliance_guard.validate_operation("pr_generation"):
        raise HTTPException(
            status_code=403,
            detail="PR generation not authorized - check compliance"
        )
    
    try:
        # Read and analyze diff
        diff_content = await diff_file.read()
        diff_text = diff_content.decode('utf-8')
        
        analysis = micro_scribe.analyze_diff(diff_text)
        
        # Generate PR template
        pr_template = micro_scribe.generate_pr(analysis, title, description)
        
        return {
            "analysis": analysis.model_dump(),
            "pr_template": pr_template.model_dump()
        }
    
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid diff file - must be UTF-8 encoded text"
        )
    except Exception as e:
        logger.error(f"PR generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"PR generation failed: {str(e)}"
        )


@router.post("/micrologician/analyze")
async def analyze_logs(log_file: UploadFile = File(...)):
    """
    Analyze log file with quantum-enhanced intelligence
    
    Upload a log file for analysis
    """
    # Check compliance
    if not compliance_guard.validate_operation("log_analysis"):
        raise HTTPException(
            status_code=403,
            detail="Log analysis not authorized - check compliance"
        )
    
    try:
        # Read log content
        log_content = await log_file.read()
        log_text = log_content.decode('utf-8')
        
        # Analyze logs
        analysis = micro_logician.analyze_logs(log_text)
        
        return analysis.model_dump()
    
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid log file - must be UTF-8 encoded text"
        )
    except Exception as e:
        logger.error(f"Log analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Log analysis failed: {str(e)}"
        )


@router.post("/micrologician/security")
async def get_security_intelligence(log_file: UploadFile = File(...)):
    """
    Get security intelligence from logs
    
    Focuses on security threats and vulnerabilities
    """
    # Check compliance
    if not compliance_guard.validate_operation("security_intelligence"):
        raise HTTPException(
            status_code=403,
            detail="Security intelligence not authorized - check compliance"
        )
    
    try:
        # Read and analyze logs
        log_content = await log_file.read()
        log_text = log_content.decode('utf-8')
        
        analysis = micro_logician.analyze_logs(log_text)
        
        # Extract security-focused data
        return {
            "threat_level": max(
                [f.threat_level for f in analysis.security_findings],
                default="NONE"
            ),
            "findings_count": len(analysis.security_findings),
            "security_findings": [f.model_dump() for f in analysis.security_findings],
            "recommendations": [
                r for r in analysis.recommendations 
                if any(keyword in r.lower() for keyword in ['security', 'critical', 'credential', 'auth'])
            ],
            "mode": analysis.mode,
            "confidence": analysis.confidence
        }
    
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid log file - must be UTF-8 encoded text"
        )
    except Exception as e:
        logger.error(f"Security intelligence failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Security intelligence failed: {str(e)}"
        )


@router.post("/micrologician/performance")
async def get_performance_metrics(log_file: UploadFile = File(...)):
    """
    Get performance metrics from logs
    
    Focuses on performance bottlenecks and optimization opportunities
    """
    # Check compliance
    if not compliance_guard.validate_operation("performance_analysis"):
        raise HTTPException(
            status_code=403,
            detail="Performance analysis not authorized - check compliance"
        )
    
    try:
        # Read and analyze logs
        log_content = await log_file.read()
        log_text = log_content.decode('utf-8')
        
        analysis = micro_logician.analyze_logs(log_text)
        
        # Extract performance-focused data
        return {
            "metrics": analysis.performance_metrics.model_dump(),
            "anomalies": [a.model_dump() for a in analysis.anomalies],
            "patterns": analysis.patterns,
            "recommendations": [
                r for r in analysis.recommendations 
                if any(keyword in r.lower() for keyword in ['performance', 'error', 'bottleneck', 'rate'])
            ],
            "mode": analysis.mode,
            "confidence": analysis.confidence
        }
    
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid log file - must be UTF-8 encoded text"
        )
    except Exception as e:
        logger.error(f"Performance analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Performance analysis failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for sovereign engines"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "engines": ["compliance_guard", "micro_scribe", "micro_logician"]
    }
