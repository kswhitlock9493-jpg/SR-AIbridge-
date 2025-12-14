import socket, time, requests, os

# Set default socket timeout to prevent hangs
socket.setdefaulttimeout(10)

def dns_warmup(host, attempts=3):
    for _ in range(attempts):
        try:
            socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
            return True
        except Exception:
            time.sleep(0.3)
    return False

def http(method, url, timeout=8, retries=3, backoff=0.5, **kw):
    last_error = None
    for i in range(retries):
        try:
            resp = requests.request(method, url, timeout=timeout, **kw)
            return resp
        except requests.exceptions.SSLError as e:
            last_error = e
            # honor custom CA if present
            cafile = os.environ.get("ACTIONS_CA_BUNDLE")
            if cafile:
                kw["verify"] = cafile
        except Exception as e:
            last_error = e
        if i < retries - 1:  # Don't sleep after the last retry
            time.sleep(backoff * (2 ** i))
    raise last_error if last_error else Exception(f"Failed to {method} {url} after {retries} retries")
