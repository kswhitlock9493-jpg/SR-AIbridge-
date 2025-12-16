# Log Signatures Reference

## Overview

This document maps common network and firewall error signatures to their root causes and recommended solutions.

## Error Signature Categories

### DNS Resolution Errors

#### `ENOTFOUND`
**Full Error:** `getaddrinfo ENOTFOUND <hostname>`

**Root Cause:**
- DNS server unreachable
- DNS query blocked by firewall
- Hostname does not exist
- DNS resolution timeout

**Solution:**
1. Allow UDP port 53 outbound
2. Verify DNS server configuration
3. Check hostname spelling
4. Add fallback DNS servers (e.g., 8.8.8.8, 1.1.1.1)

**Example:**
```
Error: getaddrinfo ENOTFOUND registry.npmjs.org
```

#### `DNS resolution failed`
**Root Cause:**
- DNS query blocked
- DNS server failure
- Network connectivity issue

**Solution:**
1. Test DNS resolution: `nslookup <hostname>`
2. Verify DNS server accessibility
3. Check firewall rules for UDP 53

---

### Connection Errors

#### `ECONNREFUSED`
**Full Error:** `connect ECONNREFUSED <ip>:<port>`

**Root Cause:**
- Service not running on target host
- Firewall blocking connection
- Wrong port number
- Service listening on different interface

**Solution:**
1. Verify service is running
2. Check firewall rules for required ports
3. Confirm correct port number
4. Test connectivity: `telnet <host> <port>`

**Example:**
```
Error: connect ECONNREFUSED 104.16.18.35:443
```

#### `ECONNRESET`
**Full Error:** `read ECONNRESET` or `socket hang up`

**Root Cause:**
- Connection forcibly closed by remote host
- Network instability
- Firewall connection tracking timeout
- Proxy/load balancer issue

**Solution:**
1. Check network stability
2. Increase connection timeout values
3. Verify firewall state tracking settings
4. Check for rate limiting

**Example:**
```
Error: read ECONNRESET
Error: socket hang up
```

#### `ETIMEDOUT`
**Full Error:** `connect ETIMEDOUT <ip>:<port>`

**Root Cause:**
- Network latency too high
- Firewall silently dropping packets
- Service unresponsive
- Connection timeout too short

**Solution:**
1. Increase timeout values
2. Check network latency: `ping <host>`
3. Verify firewall allows connection
4. Test with longer timeout: `curl --max-time 30 <url>`

**Example:**
```
Error: connect ETIMEDOUT 185.199.108.133:443
```

---

### HTTP/HTTPS Errors

#### `E404`
**Full Error:** `404 Not Found` or `npm ERR! 404`

**Root Cause:**
- Resource does not exist
- Package name misspelled
- Registry unreachable
- Proxy/cache issue

**Solution:**
1. Verify resource exists
2. Check package name spelling
3. Test registry connectivity: `curl https://registry.npmjs.org/`
4. Clear package manager cache

**Example:**
```
npm ERR! 404 Not Found - GET https://registry.npmjs.org/@types/express
```

#### `E403`
**Full Error:** `403 Forbidden`

**Root Cause:**
- Authentication required
- IP address blocked
- Rate limiting
- Insufficient permissions

**Solution:**
1. Verify authentication credentials
2. Check rate limits
3. Verify IP not blocked
4. Use authentication token if required

---

### SSL/TLS Certificate Errors

#### `self signed certificate`
**Full Error:** `unable to verify the first certificate` or `self signed certificate in certificate chain`

**Root Cause:**
- Custom/enterprise CA not trusted
- Self-signed certificate on server
- Missing intermediate certificates
- Certificate bundle incomplete

**Solution:**
1. Import enterprise CA chain
2. Set `NODE_EXTRA_CA_CERTS=/path/to/ca-bundle.crt`
3. Set `REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt`
4. Update system certificate store

**Example:**
```
Error: unable to verify the first certificate
RequestError: self signed certificate in certificate chain
```

#### `certificate verify failed`
**Full Error:** `certificate verify failed: unable to get local issuer certificate`

**Root Cause:**
- Missing CA certificates
- Outdated certificate bundle
- Corporate proxy with SSL inspection

**Solution:**
1. Update CA certificates: `update-ca-certificates`
2. Install certifi for Python: `pip install --upgrade certifi`
3. Configure proxy CA if applicable

**Example:**
```
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

---

### Network Unreachable Errors

#### `Network unreachable`
**Full Error:** `connect ENETUNREACH <ip>`

**Root Cause:**
- No route to destination
- Network interface down
- Firewall blocking all traffic
- VPN/tunnel not established

**Solution:**
1. Check network connectivity
2. Verify routing table
3. Check firewall rules
4. Verify VPN/tunnel status

**Example:**
```
Error: connect ENETUNREACH 2606:50c0:8000::154
```

#### `Host unreachable`
**Full Error:** `connect EHOSTUNREACH <ip>`

**Root Cause:**
- Host is down
- Firewall blocking ICMP
- No route to host
- Network segmentation

**Solution:**
1. Ping host to verify reachability
2. Check routing
3. Verify firewall allows traffic
4. Check network segmentation rules

---

### Package Manager Specific

#### npm Errors

**`npm ERR! code ENOTFOUND`**
```
npm ERR! code ENOTFOUND
npm ERR! errno ENOTFOUND
npm ERR! network request to https://registry.npmjs.org/... failed
```

**Solution:**
- Allow `registry.npmjs.org` and `nodejs.org`
- Verify HTTPS (port 443) access
- Check npm registry configuration: `npm config get registry`

**`npm ERR! code E404`**
```
npm ERR! 404 Not Found - GET https://registry.npmjs.org/package
```

**Solution:**
- Verify package name
- Check package exists: visit `https://www.npmjs.com/package/<name>`
- Ensure registry is accessible

#### pip Errors

**`Could not fetch URL`**
```
WARNING: Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None))
after connection broken by 'SSLError': [SSL: CERTIFICATE_VERIFY_FAILED]
Could not fetch URL https://pypi.org/simple/requests/
```

**Solution:**
- Allow `pypi.org` and `files.pythonhosted.org`
- Update CA certificates
- Set `REQUESTS_CA_BUNDLE` environment variable

---

## Firewall Signature Detection

The Firewall Intelligence Engine automatically detects these signatures:

```python
ERROR_SIGNATURES = [
    "ENOTFOUND",
    "E404",
    "ECONNRESET",
    "ETIMEDOUT",
    "ECONNREFUSED",
    "self signed certificate",
    "certificate verify failed",
    "SSL error",
    "Connection refused",
    "Network unreachable",
    "DNS resolution failed",
    "getaddrinfo ENOTFOUND",
    "blocked",
    "firewall"
]
```

## Quick Diagnostic Commands

### Test DNS
```bash
nslookup registry.npmjs.org
dig registry.npmjs.org
```

### Test Connectivity
```bash
curl -I https://registry.npmjs.org
telnet registry.npmjs.org 443
nc -zv registry.npmjs.org 443
```

### Test Package Managers
```bash
npm ping
npm install --dry-run express
pip install --dry-run requests
```

### Test SSL/TLS
```bash
openssl s_client -connect registry.npmjs.org:443
curl -v https://registry.npmjs.org 2>&1 | grep -i certificate
```

## CI/CD Specific Issues

### GitHub Actions

**Rate Limiting:**
```
Error: Resource not accessible by integration
```
- Use `GITHUB_TOKEN` with appropriate permissions
- Implement retry logic with exponential backoff

**Timeout:**
```
Error: The operation was canceled.
```
- Increase job timeout: `timeout-minutes: 30`
- Use caching to reduce build time

### Render Deployment

**Build Timeout:**
```
Build timed out after 15 minutes
```
- Optimize build process
- Use build cache
- Split large builds into stages

**Environment Variable Missing:**
```
Error: Required environment variable not set
```
- Configure variables in Render dashboard
- Use `.env` file for local development

### Netlify Deployment

**Build Failed:**
```
Build script returned non-zero exit code
```
- Check build logs for specific error
- Verify build command in `netlify.toml`
- Test build locally

## Integration with Firewall Intelligence

When these signatures are detected:

1. **Incident Collection:** Logged in `firewall_incidents.json`
2. **Analysis:** Processed by `analyze_firewall_findings.py`
3. **Recommendations:** Generated in `firewall_report.json`
4. **Allowlist:** Updated in `generated_allowlist.yaml`
5. **Severity:** Calculated based on signature count and type

## See Also

- [FIREWALL_HARDENING.md](./FIREWALL_HARDENING.md) - Network policy guide
- [FIREWALL_WATCHDOG.md](./FIREWALL_WATCHDOG.md) - Monitoring system
- [BRIDGE_HEALERS_CODE.md](./BRIDGE_HEALERS_CODE.md) - Self-healing philosophy
