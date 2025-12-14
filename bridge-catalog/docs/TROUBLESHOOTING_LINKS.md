# Troubleshooting: HXO Genesis Links

## Common Issues

### "NoneType can't be used in 'await' expression"

**Cause**: Attempting to await a sync method on the Genesis bus.

**Solution**: v1.9.6q fixes this automatically. The `maybe_await` utility handles both sync and async calls.

**If you still see this error:**
- Ensure you're calling the new `HXOGenesisLink` class methods (`.register()`, `.wire()`)
- Check that you're not using an older registration signature like `await bus.register(hxo)`
- Verify you're on v1.9.6q: `python -c "import bridge_backend; print(bridge_backend.__version__)"`

### "Invalid Genesis topic: deploy.tde.orchestrator.completed"

**Cause**: Topic not registered in Genesis bus.

**Solution**: v1.9.6q adds these topics automatically.

**If you still see warnings:**
1. Verify the topics are in `bridge_backend/genesis/bus.py`:
   ```python
   "deploy.tde.orchestrator.completed",
   "deploy.tde.orchestrator.failed",
   "autonomy.tuning.signal",
   ```
2. Check `GENESIS_STRICT_POLICY` - if set to `false`, warnings are informational only

### Import Error: "cannot import name 'notify_autonomy_autotune_signal'"

**Cause**: Old code trying to import a symbol that doesn't exist.

**Solution**: v1.9.6q removes this direct import. The link now emits Genesis events instead.

**If custom code needs this:**
- Use the new class-based API: `HXOAutonomyLink(bus, hxo).wire()`
- Or emit the event directly: `await genesis_bus.publish("autonomy.tuning.signal", payload)`

### Registration Fails on Render Startup

**Symptom**: Logs show registration errors during boot.

**Cause**: Transient timing issue (bus not ready, HXO not initialized).

**Solution**: v1.9.6q adds exponential backoff retry (6 attempts, 0.2s base delay).

**If retries still fail:**
- Check that `GENESIS_MODE=enabled` in environment
- Verify Genesis bus is initialized before HXO adapters
- Check for underlying import errors in the stack trace

## Health Checks

### Verify HXO Genesis Link is Active

1. Check logs for: `[HXO Genesis Link] ✅ Registration established`
2. Call introspection endpoint: `GET /api/genesis/health`
3. Verify HXO subscriptions:
   ```bash
   curl $API_BASE/api/genesis/stats | jq '.topics'
   ```
   Should show subscribers for:
   - `genesis.heal`
   - `deploy.tde.orchestrator.completed`
   - `deploy.tde.orchestrator.failed`

### Verify HXO Autonomy Link is Active

1. Check logs for: `[HXO-Autonomy Link] ✅ Link established`
2. Emit test signal:
   ```bash
   curl -X POST "$API_BASE/api/genesis/publish" \
     -d '{"topic":"autonomy.tuning.signal","payload":{"test":true}}' \
     -H 'Content-Type: application/json'
   ```
3. Check logs - HXO should process the signal without errors

## Debug Mode

Enable detailed Genesis tracing:

```bash
export GENESIS_TRACE_LEVEL=3  # 0=off, 1=errors, 2=info, 3=debug
```

Then check logs for:
- `📡 Genesis event [topic]: type` - Event flow
- `📡 Genesis subscription: topic` - Registration confirmation

## Getting Help

If issues persist:
1. Collect full stack trace from logs
2. Note Render deployment timestamp
3. Check `GENESIS_MODE`, `GENESIS_STRICT_POLICY` env vars
4. Verify version: `python -c "import bridge_backend; print(bridge_backend.__version__)"`
5. Open issue with above details
