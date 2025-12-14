#!/usr/bin/env python3
import json, pathlib, time, datetime, subprocess, requests

VAULT      = pathlib.Path("vault")
INTENTIONS = VAULT / "coefficient-spectrum"
SNAPSHOT   = VAULT / "reality_snapshot.json"
LOG        = VAULT / "verify_log.jsonl"

def get_github_metrics():
    # replace with your repo
    r = requests.get("https://api.github.com/repos/kswhitlock9493-jpg/SR-AIbridge-")
    if r.status_code == 200:
        data = r.json()
        return {"github_stars": data["stargazers_count"],
                "forks": data["forks_count"],
                "open_issues": data["open_issues_count"]}
    return {"github_stars": 0, "forks": 0, "open_issues": 0}

def load_tests():
    tests = []
    for f in INTENTIONS.glob("*.json"):
        body = json.loads(f.read_text())
        tests.extend(body["pathway"]["verification_tests"])
    return tests

def evaluate(tests, reality):
    for t in tests:
        metric, op, val = t["metric"], t["operator"], t["value"]
        actual = reality.get(metric, 0)
        if op == ">=" and actual < val:
            return False, f"{metric} {actual} < {val}"
        if op == "<=" and actual > val:
            return False, f"{metric} {actual} > {val}"
    return True, "all green"

def log(result, detail):
    entry = {"timestamp": datetime.datetime.utcnow().isoformat() + "Z",
             "result": result, "detail": detail}
    with LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")

def open_issue(title):
    subprocess.run([
        "gh", "issue", "create",
        "--title", title,
        "--body", "Resonance-drift detected by continuous verify loop.",
        "--label", "resonance-drift"
    ])

def main():
    reality = get_github_metrics()
    SNAPSHOT.write_text(json.dumps(reality, indent=2))
    tests = load_tests()
    ok, detail = evaluate(tests, reality)
    log(ok, detail)
    if not ok:
        open_issue(f"Resonance-drift: {detail}")

if __name__ == "__main__":
    main()
