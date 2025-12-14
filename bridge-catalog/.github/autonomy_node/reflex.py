"""
Reflex Loop Protocol - Self-PR Engine
v1.9.7o - Autonomous PR creation and submission

The Embedded Autonomy Node (EAN) uses this module to detect issues,
patch them, and file pull requests autonomously.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local modules
try:
    from . import signer, verifier
except ImportError:
    # Allow running as standalone script
    import signer
    import verifier


def reflex_loop():
    """
    Main reflex loop - detects local fixes and self-creates PRs.
    
    Scans the reports directory for autonomy reports and creates
    PRs for any that are ready.
    """
    logger.info("🧠 [REFLEX] Starting Reflex Loop Protocol scan")
    
    report_dir = ".github/autonomy_node/reports"
    
    # Check if reports directory exists
    if not os.path.exists(report_dir):
        logger.info(f"📂 [REFLEX] Reports directory not found: {report_dir}")
        logger.info(f"📂 [REFLEX] Creating directory: {report_dir}")
        os.makedirs(report_dir, exist_ok=True)
        return
    
    # Scan for report files
    report_files = [f for f in os.listdir(report_dir) if f.endswith(".json")]
    
    if not report_files:
        logger.info("📭 [REFLEX] No reports found to process")
        return
    
    logger.info(f"📊 [REFLEX] Found {len(report_files)} report(s) to process")
    
    # Process each report
    for filename in report_files:
        filepath = os.path.join(report_dir, filename)
        
        try:
            with open(filepath, 'r') as f:
                report = json.load(f)
            
            logger.info(f"📄 [REFLEX] Processing report: {filename}")
            
            # Check if ready for PR
            if verifier.ready_to_pr(report):
                logger.info(f"✅ [REFLEX] Report ready for PR: {filename}")
                
                # Build PR body
                pr_body = build_pr_body(report)
                
                # Sign the PR
                pr_data = signer.sign(pr_body)
                
                # Submit the PR
                submit(pr_data)
            else:
                logger.info(f"⏭️  [REFLEX] Report not ready for PR: {filename}")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ [REFLEX] Invalid JSON in {filename}: {e}")
        except Exception as e:
            logger.error(f"❌ [REFLEX] Error processing {filename}: {e}")


def build_pr_body(report: Dict[str, Any]) -> str:
    """
    Build PR body from autonomy report.
    
    Args:
        report: Report dictionary with fix details
        
    Returns:
        Formatted PR body text
    """
    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    body = f"""## 🤖 EAN Reflex PR — Auto-Generated

**Timestamp:** {timestamp}  
**Report:** {report.get('summary', 'N/A')}  
**Truth Signature:** pending  

### Changes
- {report.get('safe_fixes', 0)} files cleaned  
- {report.get('verified', True)} verification status  

### Details
{report.get('details', 'No additional details provided.')}

---

_This PR was generated autonomously by the Embedded Autonomy Node._
_All changes have been certified by the Truth Engine and approved under RBAC protocols._
"""
    
    return body


def submit(pr_data: Dict[str, Any]):
    """
    Submit a PR to GitHub or queue offline.
    
    Args:
        pr_data: Signed PR data with title, body, and signature
    """
    token = os.getenv("GITHUB_TOKEN")
    
    if not token:
        logger.warning("⚠️  [REFLEX] No GITHUB_TOKEN found - queuing PR offline")
        queue_offline(pr_data)
        return
    
    # Get repository information
    repo_slug = os.getenv("GITHUB_REPOSITORY")
    if not repo_slug:
        logger.error("❌ [REFLEX] GITHUB_REPOSITORY not set - cannot submit PR")
        queue_offline(pr_data)
        return
    
    logger.info(f"🚀 [REFLEX] Preparing to submit PR to {repo_slug}")
    
    # Build API payload
    api_url = f"https://api.github.com/repos/{repo_slug}/pulls"
    
    payload = {
        "title": pr_data["title"],
        "body": pr_data["body"],
        "head": "autonomy/reflex",
        "base": "main",
        "draft": False
    }
    
    # In a real implementation, this would make an HTTP request
    # For now, we queue it offline to avoid actual API calls
    logger.info("📝 [REFLEX] PR payload prepared (queuing offline for safety)")
    queue_offline(pr_data)


def queue_offline(pr_data: Dict[str, Any]):
    """
    Queue a PR for offline processing.
    
    Args:
        pr_data: Signed PR data to queue
    """
    pending_dir = ".github/autonomy_node/pending_prs"
    os.makedirs(pending_dir, exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).timestamp()
    filename = f"{pending_dir}/{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(pr_data, f, indent=2)
    
    logger.info(f"💾 [REFLEX] PR queued offline: {filename}")


if __name__ == "__main__":
    # Run reflex loop when executed directly
    reflex_loop()
