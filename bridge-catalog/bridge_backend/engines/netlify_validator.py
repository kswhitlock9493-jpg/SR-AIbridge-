"""
Netlify Validator Engine
Local syntax & semantic validator for Netlify configurations
Part of Umbra + Netlify Integration v1.9.7e
"""

import subprocess
import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class NetlifyValidator:
    """
    Netlify Configuration Validator
    
    Runs local validation of Netlify configs and integrates with Umbra for learning
    """
    
    def __init__(self, truth=None, umbra_memory=None):
        """
        Initialize Netlify Validator
        
        Args:
            truth: Truth Engine instance for certification (optional)
            umbra_memory: Umbra Memory instance for learning (optional)
        """
        self.truth = truth
        self.umbra_memory = umbra_memory
        self.enabled = os.getenv("NETLIFY_OPTIONAL_PREVIEW_CHECKS", "true").lower() == "true"
        
        logger.info("🌐 Netlify Validator initialized")
    
    async def validate_rules(self) -> Dict[str, Any]:
        """
        Local syntax & semantic validator
        
        Returns:
            Validation result with status and details
        """
        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "unknown",
            "output": "",
            "error": None,
            "certified": False
        }
        
        try:
            # Run validation script
            proc_result = subprocess.run(
                ["python3", "scripts/validate_netlify.py"],
                capture_output=True,
                text=True,
                check=True
            )
            
            result["status"] = "success"
            result["output"] = proc_result.stdout
            
            logger.info("🌐 Netlify validation passed")
            
            # Record to Umbra Memory if available
            if self.umbra_memory:
                await self.umbra_memory.record(
                    "netlify_validation",
                    {"action": "validate_rules"},
                    result
                )
            
            # Certify with Truth Engine if available
            if self.truth:
                try:
                    certified = await self.truth.certify({
                        "type": "netlify_validation",
                        "result": result
                    })
                    result["certified"] = certified.get("certified", False)
                    result["signature"] = certified.get("signature")
                except Exception as e:
                    logger.warning(f"Truth certification failed: {e}")
            
        except subprocess.CalledProcessError as e:
            result["status"] = "failed"
            result["error"] = e.stderr
            result["output"] = e.stdout
            
            logger.error(f"🌐 Netlify validation failed: {e.stderr}")
            
            # Record failure to Umbra Memory for learning
            if self.umbra_memory:
                await self.umbra_memory.record(
                    "netlify_validation",
                    {"action": "validate_rules"},
                    result
                )
        
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            
            logger.error(f"🌐 Netlify validation error: {e}")
        
        return result
    
    async def validate_with_recall(self) -> Dict[str, Any]:
        """
        Validate with Umbra Memory recall
        
        Checks if similar validation failures occurred before and applies fixes
        
        Returns:
            Validation result with recall information
        """
        result = await self.validate_rules()
        
        if result["status"] != "success" and self.umbra_memory:
            # Recall similar failures
            try:
                experiences = await self.umbra_memory.recall(
                    category="netlify_validation",
                    limit=5
                )
                
                # Find successful fixes
                successful_fixes = [
                    exp for exp in experiences
                    if exp.get("result", {}).get("status") == "success"
                ]
                
                result["recall"] = {
                    "similar_failures": len(experiences),
                    "successful_fixes": len(successful_fixes),
                    "latest_fix": successful_fixes[0] if successful_fixes else None
                }
                
                logger.info(f"🧠 Recalled {len(experiences)} similar Netlify validation experiences")
                
            except Exception as e:
                logger.warning(f"Umbra recall failed: {e}")
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get validator metrics"""
        return {
            "enabled": self.enabled,
            "truth_available": self.truth is not None,
            "memory_available": self.umbra_memory is not None
        }


def validate_netlify_rules():
    """
    Standalone validation function for backward compatibility
    Local syntax & semantic validator
    
    Returns:
        Validation result dictionary
    """
    try:
        result = subprocess.run(
            ["python3", "scripts/validate_netlify.py"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Try to certify if truth is available
        try:
            from bridge_backend.genesis.bus import genesis_bus
            
            # Simple certification event
            genesis_bus.publish_sync("netlify.validation", {
                "status": "passed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        except Exception:
            pass  # Truth certification optional
        
        return {"status": "success", "output": result.stdout}
        
    except subprocess.CalledProcessError as e:
        # Try to certify failure
        try:
            from bridge_backend.genesis.bus import genesis_bus
            
            genesis_bus.publish_sync("netlify.validation", {
                "status": "failed",
                "error": e.stderr,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        except Exception:
            pass
        
        return {"status": "failed", "error": e.stderr}
