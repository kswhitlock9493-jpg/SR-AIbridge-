"""
Test Autonomy Genesis Link
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from bridge_backend.bridge_core.engines.adapters.autonomy_genesis_link import (
    on_netlify_preview_failed,
    on_render_deploy_failed,
    on_envrecon_drift,
    on_arie_deprecated_detected,
    register_autonomy_genesis_links
)


class TestAutonomyGenesisLink:
    """Test Autonomy Genesis event subscriptions"""
    
    @pytest.mark.asyncio
    async def test_on_netlify_preview_failed(self):
        """Test handling of Netlify preview failure event"""
        event = {
            "platform": "netlify",
            "status": "failed",
            "run_id": "12345"
        }
        
        # Should not raise exception
        await on_netlify_preview_failed(event)
    
    @pytest.mark.asyncio
    async def test_on_render_deploy_failed(self):
        """Test handling of Render deploy failure event"""
        event = {
            "platform": "render",
            "status": "failed",
            "deploy_id": "67890"
        }
        
        # Should not raise exception
        await on_render_deploy_failed(event)
    
    @pytest.mark.asyncio
    async def test_on_envrecon_drift(self):
        """Test handling of EnvRecon drift event"""
        event = {
            "drift_count": 3,
            "missing_vars": ["VAR1", "VAR2"]
        }
        
        # Should not raise exception
        await on_envrecon_drift(event)
    
    @pytest.mark.asyncio
    async def test_on_arie_deprecated_detected(self):
        """Test handling of ARIE deprecation event"""
        event = {
            "deprecated_count": 1,
            "files": ["old_module.py"]
        }
        
        # Should not raise exception
        await on_arie_deprecated_detected(event)
    
    def test_register_autonomy_genesis_links(self):
        """Test that Genesis link registration doesn't crash"""
        # This should succeed even if Genesis is disabled
        register_autonomy_genesis_links()
    
    @pytest.mark.asyncio
    @patch('bridge_backend.bridge_core.engines.adapters.autonomy_genesis_link.AutonomyGovernor')
    async def test_event_handler_calls_governor(self, mock_governor_class):
        """Test that event handlers call the Governor correctly"""
        mock_gov = Mock()
        mock_gov.decide = AsyncMock(return_value=Mock(action="NOOP", reason="test"))
        mock_gov.execute = AsyncMock(return_value={"status": "skipped"})
        mock_governor_class.return_value = mock_gov
        
        event = {"test": "data"}
        
        await on_netlify_preview_failed(event)
        
        # Verify governor was instantiated
        mock_governor_class.assert_called_once()
        
        # Verify decide was called
        assert mock_gov.decide.call_count == 1
        
        # Verify execute was called
        assert mock_gov.execute.call_count == 1
