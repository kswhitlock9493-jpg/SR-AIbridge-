# Stripe Webhook Integration

## Overview

The Stripe webhook integration provides secure handling of Stripe subscription events and automatically triggers Cascade Engine updates. Stripe acts as a signal provider, while Cascade remains the authoritative source of truth for permissions and tiers.

## Architecture

```
Stripe → Webhook (signature verification) → Cascade Engine → vault/cascade/patches.jsonl
```

## Setup

### 1. Environment Variables

Set the following environment variables:

```bash
STRIPE_SECRET=sk_test_...           # Stripe API secret key
STRIPE_WEBHOOK_SECRET=whsec_...    # Stripe webhook signing secret
```

### 2. Webhook Endpoint

The webhook endpoint is automatically registered at:
```
POST /payments/stripe/webhook
```

### 3. Configure Stripe

In your Stripe dashboard:
1. Navigate to Developers → Webhooks
2. Add endpoint: `https://your-domain.com/payments/stripe/webhook`
3. Select events:
   - `customer.subscription.created`
   - `customer.subscription.deleted`
   - `customer.subscription.updated`
4. Copy the signing secret to `STRIPE_WEBHOOK_SECRET`

## Supported Events

### customer.subscription.created
Triggered when a customer creates a new subscription.
- Sets tier to `"paid"`
- Requires `captain_id` in subscription metadata

### customer.subscription.deleted
Triggered when a subscription is cancelled.
- Sets tier to `"free"`
- Requires `captain_id` in subscription metadata

### customer.subscription.updated
Triggered when subscription status changes.
- Sets tier to `"paid"` if status is `"active"`
- Sets tier to `"free"` for other statuses
- Requires `captain_id` in subscription metadata

## Metadata Requirements

All Stripe subscription objects must include the following metadata:

```json
{
  "captain_id": "unique_user_identifier"
}
```

## Security

### Signature Verification

All webhook requests are verified using Stripe's signature verification:

```python
stripe.Webhook.construct_event(
    payload=payload,
    sig_header=sig_header,
    secret=STRIPE_WEBHOOK_SECRET
)
```

Requests with invalid signatures are rejected with HTTP 400.

### Source Provenance

All Cascade patches include source tracking:

```json
{
  "captain_id": "12345",
  "tier": "paid",
  "timestamp": "2025-10-03T18:22:11Z",
  "source": "stripe_webhook"
}
```

## Audit Trail

### patches.jsonl

Append-only JSONL file for audit purposes:
- Location: `vault/cascade/patches.jsonl`
- Format: One JSON object per line
- Fields: `captain_id`, `tier`, `timestamp`, `source`

### cascade_state.json

Complete history of all patches:
- Location: `vault/cascade/cascade_state.json`
- Format: JSON with `history` array
- Includes full patch details and metadata

## Example Usage

### Creating a Stripe Subscription with Metadata

```python
import stripe

subscription = stripe.Subscription.create(
    customer="cus_...",
    items=[{"price": "price_..."}],
    metadata={
        "captain_id": "user_12345"  # Required for webhook processing
    }
)
```

### Testing Locally

Use Stripe CLI to forward webhooks to localhost:

```bash
stripe listen --forward-to localhost:8000/payments/stripe/webhook
stripe trigger customer.subscription.created
```

### Verifying Cascade Updates

Check the Cascade history endpoint:

```bash
curl http://localhost:8000/engines/cascade/history
```

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Invalid signature | HTTP 400 with `invalid_signature` detail |
| Missing `captain_id` | HTTP 200, no Cascade update |
| Unknown event type | HTTP 200, no Cascade update |
| Valid event | HTTP 200, Cascade updated |

## Future Enhancements

The webhook architecture supports plugging in additional payment providers:
- PayPal
- Cryptocurrency wallets
- Custom credit systems

All providers send patches to Cascade, maintaining a single source of truth.

## Testing

Run the test suite:

```bash
cd bridge_backend
pytest tests/test_stripe_webhook.py -v
```

Tests cover:
- Signature verification
- Event handling (created, deleted, updated)
- Missing metadata handling
- Unknown event types
- Cascade integration
- patches.jsonl creation
