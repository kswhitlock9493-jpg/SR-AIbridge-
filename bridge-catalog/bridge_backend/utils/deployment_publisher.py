"""
Deployment Event Publisher
Publishes deployment events to Genesis bus for autonomy engine integration
"""

import asyncio
import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime, UTC
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure the bridge_backend is in the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


async def publish_deployment_event(
    platform: str,
    event_type: str,
    status: str = "unknown",
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Publish a deployment event to the Genesis bus.
    
    Args:
        platform: Deployment platform (netlify, render, github)
        event_type: Event type (start, success, failure, progress)
        status: Deployment status
        metadata: Additional deployment metadata
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            logger.info("Genesis bus disabled, skipping deployment event")
            return
        
        # Construct event payload
        event = {
            "platform": platform,
            "event_type": event_type,
            "status": status,
            "timestamp": datetime.now(UTC).isoformat(),
            "metadata": metadata or {}
        }
        
        # Publish to platform-specific topic
        topic = f"deploy.{platform.lower()}"
        await genesis_bus.publish(topic, event)
        logger.info(f"✅ Published deployment event to {topic}: {event_type}")
        
        # Also publish to generic deployment topic based on event type
        if event_type in ["start", "starting", "initiated"]:
            await genesis_bus.publish("deploy.platform.start", event)
        elif event_type in ["success", "completed", "deployed"]:
            await genesis_bus.publish("deploy.platform.success", event)
        elif event_type in ["failure", "failed", "error"]:
            await genesis_bus.publish("deploy.platform.failure", event)
        
    except Exception as e:
        logger.error(f"Failed to publish deployment event: {e}")
        # Don't fail the deployment if event publishing fails


def publish_deployment_event_sync(
    platform: str,
    event_type: str,
    status: str = "unknown",
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Synchronous wrapper for publish_deployment_event.
    Useful for calling from non-async contexts like shell scripts.
    """
    try:
        asyncio.run(publish_deployment_event(platform, event_type, status, metadata))
    except Exception as e:
        logger.error(f"Failed to publish deployment event (sync): {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Publish deployment events to Genesis bus")
    parser.add_argument("--platform", required=True, choices=["netlify", "render", "github"],
                        help="Deployment platform")
    parser.add_argument("--event-type", required=True,
                        help="Event type (start, success, failure, progress)")
    parser.add_argument("--status", default="unknown",
                        help="Deployment status")
    parser.add_argument("--commit-sha", help="Git commit SHA")
    parser.add_argument("--branch", help="Git branch name")
    parser.add_argument("--deploy-url", help="Deployment URL")
    parser.add_argument("--message", help="Deployment message")
    
    args = parser.parse_args()
    
    # Build metadata from arguments
    metadata = {}
    if args.commit_sha:
        metadata["commit_sha"] = args.commit_sha
    if args.branch:
        metadata["branch"] = args.branch
    if args.deploy_url:
        metadata["deploy_url"] = args.deploy_url
    if args.message:
        metadata["message"] = args.message
    
    # Publish the event
    publish_deployment_event_sync(
        platform=args.platform,
        event_type=args.event_type,
        status=args.status,
        metadata=metadata
    )
    
    print(f"✅ Deployment event published: {args.platform} - {args.event_type}")
