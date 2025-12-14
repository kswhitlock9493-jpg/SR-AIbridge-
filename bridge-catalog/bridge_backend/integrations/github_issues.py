import os, logging, httpx

log = logging.getLogger(__name__)

def _cfg():
    repo = os.getenv("GITHUB_REPO")           # e.g. "kswhitlock9493-jpg/SR-AIbridge-"
    token = os.getenv("GITHUB_TOKEN")          # classic or fine-grained with repo:issues
    if not repo or not token:
        return None, None
    return repo, token

def maybe_create_issue(title: str, body: str, labels=None):
    repo, token = _cfg()
    if not (repo and token):
        log.info("github: repo/token not set; skipping issue creation")
        return None

    url = f"https://api.github.com/repos/{repo}/issues"
    payload = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels
    try:
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
        with httpx.Client(timeout=10) as client:
            r = client.post(url, json=payload, headers=headers)
            if r.status_code in (200,201):
                iid = r.json().get("number")
                log.info(f"github: ✅ created issue #{iid}")
                return {"issue_number": iid, "url": r.json().get("html_url")}
            else:
                log.warning(f"github: issue create failed: {r.status_code} {r.text}")
    except Exception as e:
        log.warning(f"github: issue create error: {e!r}")
    return None
