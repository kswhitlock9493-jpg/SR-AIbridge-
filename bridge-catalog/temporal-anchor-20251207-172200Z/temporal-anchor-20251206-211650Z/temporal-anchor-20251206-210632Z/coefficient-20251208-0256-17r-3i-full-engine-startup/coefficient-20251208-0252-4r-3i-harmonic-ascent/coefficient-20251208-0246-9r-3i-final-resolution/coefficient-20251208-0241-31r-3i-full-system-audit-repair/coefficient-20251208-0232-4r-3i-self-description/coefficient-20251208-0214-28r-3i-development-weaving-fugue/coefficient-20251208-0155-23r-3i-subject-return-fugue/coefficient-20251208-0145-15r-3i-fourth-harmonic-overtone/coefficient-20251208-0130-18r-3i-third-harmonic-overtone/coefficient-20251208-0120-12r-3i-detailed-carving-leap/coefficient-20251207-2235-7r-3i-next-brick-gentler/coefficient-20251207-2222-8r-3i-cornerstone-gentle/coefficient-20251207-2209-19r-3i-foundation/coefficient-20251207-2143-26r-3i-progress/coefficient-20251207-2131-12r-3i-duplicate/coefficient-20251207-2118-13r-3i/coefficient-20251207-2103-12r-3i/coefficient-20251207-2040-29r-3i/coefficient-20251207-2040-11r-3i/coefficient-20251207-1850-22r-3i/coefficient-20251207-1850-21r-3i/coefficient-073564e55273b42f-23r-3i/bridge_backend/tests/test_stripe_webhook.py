from fastapi.testclient import TestClient
from main import app
import json
import pytest
from unittest.mock import patch as mock_patch, MagicMock

client = TestClient(app)


class TestStripeWebhook:
    """Test Stripe webhook integration with Cascade Engine"""

    def test_invalid_signature(self, tmp_path, monkeypatch):
        """Test that invalid signatures are rejected"""
        from bridge_core.engines.cascade import service
        monkeypatch.setattr(service, "VAULT_CASCADE", tmp_path)
        
        # Mock stripe.Webhook.construct_event to raise an exception
        with mock_patch('bridge_core.payments.stripe_webhooks.stripe.Webhook.construct_event') as mock_construct:
            mock_construct.side_effect = Exception("Invalid signature")
            
            r = client.post(
                "/payments/stripe/webhook",
                data="{}",
                headers={"stripe-signature": "bad_signature"}
            )
            assert r.status_code == 400
            assert "invalid_signature" in r.json()["detail"]

    def test_subscription_created(self, tmp_path, monkeypatch):
        """Test customer.subscription.created event"""
        from bridge_core.engines.cascade import service
        from bridge_core.payments import stripe_webhooks
        
        # Monkeypatch both the service module and the import in stripe_webhooks
        monkeypatch.setattr(service, "VAULT_CASCADE", tmp_path)
        
        # Mock the stripe webhook verification
        event = {
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "metadata": {
                        "captain_id": "test_captain"
                    }
                }
            }
        }
        
        with mock_patch('bridge_core.payments.stripe_webhooks.stripe.Webhook.construct_event') as mock_construct:
            mock_construct.return_value = event
            
            # We need to also patch the CascadeEngine import in the webhook handler
            with mock_patch('bridge_core.payments.stripe_webhooks.CascadeEngine') as MockEngine:
                C = service.CascadeEngine(tmp_path)
                MockEngine.return_value = C
                
                r = client.post(
                    "/payments/stripe/webhook",
                    data=json.dumps(event),
                    headers={"stripe-signature": "valid_signature"}
                )
                assert r.status_code == 200
                assert r.json() == {"ok": True}
            
                # Verify the cascade engine was updated
                history = C.history()
                assert len(history["history"]) > 0
                latest = history["history"][-1]
                assert latest["captain_id"] == "test_captain"
                assert latest["patch"]["tier"] == "paid"
                assert latest.get("source") == "stripe_webhook"

    def test_subscription_deleted(self, tmp_path, monkeypatch):
        """Test customer.subscription.deleted event"""
        from bridge_core.engines.cascade import service
        
        monkeypatch.setattr(service, "VAULT_CASCADE", tmp_path)
        
        # Mock the stripe webhook verification
        event = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "metadata": {
                        "captain_id": "test_captain_2"
                    }
                }
            }
        }
        
        with mock_patch('bridge_core.payments.stripe_webhooks.stripe.Webhook.construct_event') as mock_construct:
            mock_construct.return_value = event
            
            with mock_patch('bridge_core.payments.stripe_webhooks.CascadeEngine') as MockEngine:
                C = service.CascadeEngine(tmp_path)
                MockEngine.return_value = C
                
                r = client.post(
                    "/payments/stripe/webhook",
                    data=json.dumps(event),
                    headers={"stripe-signature": "valid_signature"}
                )
                assert r.status_code == 200
                assert r.json() == {"ok": True}
            
                # Verify the cascade engine was updated
                history = C.history()
                assert len(history["history"]) > 0
                latest = history["history"][-1]
                assert latest["captain_id"] == "test_captain_2"
                assert latest["patch"]["tier"] == "free"
                assert latest.get("source") == "stripe_webhook"

    def test_subscription_updated_active(self, tmp_path, monkeypatch):
        """Test customer.subscription.updated event with active status"""
        from bridge_core.engines.cascade import service
        
        monkeypatch.setattr(service, "VAULT_CASCADE", tmp_path)
        
        # Mock the stripe webhook verification
        event = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "metadata": {
                        "captain_id": "test_captain_3"
                    },
                    "status": "active"
                }
            }
        }
        
        with mock_patch('bridge_core.payments.stripe_webhooks.stripe.Webhook.construct_event') as mock_construct:
            mock_construct.return_value = event
            
            with mock_patch('bridge_core.payments.stripe_webhooks.CascadeEngine') as MockEngine:
                C = service.CascadeEngine(tmp_path)
                MockEngine.return_value = C
                
                r = client.post(
                    "/payments/stripe/webhook",
                    data=json.dumps(event),
                    headers={"stripe-signature": "valid_signature"}
                )
                assert r.status_code == 200
                assert r.json() == {"ok": True}
            
                # Verify the cascade engine was updated
                history = C.history()
                assert len(history["history"]) > 0
                latest = history["history"][-1]
                assert latest["captain_id"] == "test_captain_3"
                assert latest["patch"]["tier"] == "paid"
                assert latest.get("source") == "stripe_webhook"

    def test_subscription_updated_cancelled(self, tmp_path, monkeypatch):
        """Test customer.subscription.updated event with cancelled status"""
        from bridge_core.engines.cascade import service
        
        monkeypatch.setattr(service, "VAULT_CASCADE", tmp_path)
        
        # Mock the stripe webhook verification
        event = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "metadata": {
                        "captain_id": "test_captain_4"
                    },
                    "status": "canceled"
                }
            }
        }
        
        with mock_patch('bridge_core.payments.stripe_webhooks.stripe.Webhook.construct_event') as mock_construct:
            mock_construct.return_value = event
            
            with mock_patch('bridge_core.payments.stripe_webhooks.CascadeEngine') as MockEngine:
                C = service.CascadeEngine(tmp_path)
                MockEngine.return_value = C
                
                r = client.post(
                    "/payments/stripe/webhook",
                    data=json.dumps(event),
                    headers={"stripe-signature": "valid_signature"}
                )
                assert r.status_code == 200
                assert r.json() == {"ok": True}
            
                # Verify the cascade engine was updated
                history = C.history()
                assert len(history["history"]) > 0
                latest = history["history"][-1]
                assert latest["captain_id"] == "test_captain_4"
                assert latest["patch"]["tier"] == "free"
                assert latest.get("source") == "stripe_webhook"

    def test_missing_captain_id(self, tmp_path, monkeypatch):
        """Test that events without captain_id are handled gracefully"""
        from bridge_core.engines.cascade import service
        monkeypatch.setattr(service, "VAULT_CASCADE", tmp_path)
        
        # Mock the stripe webhook verification
        event = {
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "metadata": {}
                }
            }
        }
        
        with mock_patch('bridge_core.payments.stripe_webhooks.stripe.Webhook.construct_event') as mock_construct:
            mock_construct.return_value = event
            
            r = client.post(
                "/payments/stripe/webhook",
                data=json.dumps(event),
                headers={"stripe-signature": "valid_signature"}
            )
            # Should still return 200, but not create any cascade entry
            assert r.status_code == 200
            assert r.json() == {"ok": True}

    def test_unknown_event_type(self, tmp_path, monkeypatch):
        """Test that unknown event types are handled gracefully"""
        from bridge_core.engines.cascade import service
        monkeypatch.setattr(service, "VAULT_CASCADE", tmp_path)
        
        # Mock the stripe webhook verification
        event = {
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "metadata": {
                        "captain_id": "test_captain"
                    }
                }
            }
        }
        
        with mock_patch('bridge_core.payments.stripe_webhooks.stripe.Webhook.construct_event') as mock_construct:
            mock_construct.return_value = event
            
            r = client.post(
                "/payments/stripe/webhook",
                data=json.dumps(event),
                headers={"stripe-signature": "valid_signature"}
            )
            # Should still return 200, but not create any cascade entry
            assert r.status_code == 200
            assert r.json() == {"ok": True}

    def test_patches_jsonl_created(self, tmp_path, monkeypatch):
        """Test that patches.jsonl is created and written to"""
        from bridge_core.engines.cascade import service
        
        monkeypatch.setattr(service, "VAULT_CASCADE", tmp_path)
        
        # Mock the stripe webhook verification
        event = {
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "metadata": {
                        "captain_id": "test_captain_jsonl"
                    }
                }
            }
        }
        
        with mock_patch('bridge_core.payments.stripe_webhooks.stripe.Webhook.construct_event') as mock_construct:
            mock_construct.return_value = event
            
            with mock_patch('bridge_core.payments.stripe_webhooks.CascadeEngine') as MockEngine:
                C = service.CascadeEngine(tmp_path)
                MockEngine.return_value = C
                
                r = client.post(
                    "/payments/stripe/webhook",
                    data=json.dumps(event),
                    headers={"stripe-signature": "valid_signature"}
                )
                assert r.status_code == 200
            
                # Verify patches.jsonl exists and contains the entry
                patches_file = tmp_path / "patches.jsonl"
                assert patches_file.exists()
                
                with open(patches_file, "r") as f:
                    lines = f.readlines()
                    assert len(lines) > 0
                    patch_record = json.loads(lines[-1])
                    assert patch_record["captain_id"] == "test_captain_jsonl"
                    assert patch_record["tier"] == "paid"
                    assert patch_record["source"] == "stripe_webhook"
                    assert "timestamp" in patch_record

