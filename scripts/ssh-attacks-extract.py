#!/usr/bin/env python3
"""Extract SSH brute-force attempts from journalctl, enrich with geo, write attacks.json."""
import json
import re
import subprocess
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).parent / "attacks.json"
GEO_CACHE = Path(__file__).parent / "geo_cache.json"
DAYS = 30

LINE_RE = re.compile(
    r"^(?P<ts>\S+)\s+\S+\s+sshd\[\d+\]:\s+"
    r"(?:Invalid user (?P<user>\S+)|Failed password for (?:invalid user )?(?P<user2>\S+))"
    r".*?from (?P<ip>\d+\.\d+\.\d+\.\d+)"
)

# SSH usernames are attacker-controlled and end up in attacks.json verbatim,
# which is then rendered by client-side JS. Defense in depth: drop control
# chars, allow only a conservative printable subset, cap length. The dashboard
# also escapes on render, but pre-sanitizing keeps the JSON readable.
SAFE_USER_RE = re.compile(r"[^A-Za-z0-9._\-]")
MAX_USER_LEN = 32


def sanitize_user(u):
    if not u:
        return "?"
    cleaned = SAFE_USER_RE.sub("?", u)[:MAX_USER_LEN]
    return cleaned or "?"


def load_cache():
    if GEO_CACHE.exists():
        return json.loads(GEO_CACHE.read_text())
    return {}


def save_cache(c):
    GEO_CACHE.write_text(json.dumps(c, indent=1))


def geo_lookup(ip, cache):
    if ip in cache:
        return cache[ip]
    url = f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,regionName,city,lat,lon,isp,org,as"
    try:
        with urllib.request.urlopen(url, timeout=4) as r:
            data = json.loads(r.read())
        if data.get("status") == "success":
            cache[ip] = {
                "country": data.get("country", "?"),
                "cc": data.get("countryCode", "??"),
                "region": data.get("regionName", ""),
                "city": data.get("city", ""),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "isp": data.get("isp", ""),
                "org": data.get("org", ""),
                "asn": data.get("as", ""),
            }
        else:
            cache[ip] = {"country": "Unknown", "cc": "??", "lat": None, "lon": None, "isp": "", "org": "", "asn": ""}
    except Exception as e:
        print(f"geo fail {ip}: {e}", file=sys.stderr)
        cache[ip] = {"country": "Unknown", "cc": "??", "lat": None, "lon": None, "isp": "", "org": "", "asn": ""}
    return cache[ip]


def get_home(cache):
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=4) as r:
            ip = r.read().decode().strip()
    except Exception:
        return None
    g = geo_lookup(ip, cache)
    return {"ip": ip, **g}


def main():
    print("[*] reading journalctl...", file=sys.stderr)
    cmd = ["sudo", "journalctl", "-u", "ssh", "-S", f"{DAYS} days ago", "-o", "short-iso", "--no-pager"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    lines = proc.stdout.splitlines()
    print(f"[*] {len(lines)} log lines", file=sys.stderr)

    events = []
    for ln in lines:
        m = LINE_RE.search(ln)
        if not m:
            continue
        ts = m.group("ts")
        user = m.group("user") or m.group("user2")
        ip = m.group("ip")
        try:
            dt = datetime.fromisoformat(ts).astimezone(timezone.utc)
        except ValueError:
            continue
        events.append({"ts": dt.isoformat(), "epoch": int(dt.timestamp()), "user": sanitize_user(user), "ip": ip})

    print(f"[*] {len(events)} brute-force events parsed", file=sys.stderr)

    ip_counts = Counter(e["ip"] for e in events)
    user_counts = Counter(e["user"] for e in events)

    cache = load_cache()
    unique_ips = list(ip_counts.keys())
    print(f"[*] {len(unique_ips)} unique IPs, geo-looking up...", file=sys.stderr)

    n_new = 0
    for i, ip in enumerate(unique_ips):
        if ip not in cache:
            geo_lookup(ip, cache)
            n_new += 1
            if n_new % 40 == 0:
                save_cache(cache)
                time.sleep(60)
        else:
            geo_lookup(ip, cache)
    save_cache(cache)
    print(f"[*] {n_new} new geo lookups", file=sys.stderr)

    hourly = Counter()
    for e in events:
        bucket = e["epoch"] - (e["epoch"] % 3600)
        hourly[bucket] += 1

    country_counts = Counter()
    for ip, n in ip_counts.items():
        cc = cache.get(ip, {}).get("cc", "??")
        country_counts[cc] += n

    home = get_home(cache)
    save_cache(cache)

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_days": DAYS,
        "home": home,
        "total_attempts": len(events),
        "unique_ips": len(unique_ips),
        "unique_countries": len([c for c in country_counts if c != "??"]),
        "hourly": [{"t": t, "n": n} for t, n in sorted(hourly.items())],
        "top_ips": [
            {
                "ip": ip,
                "count": n,
                **cache.get(ip, {}),
            }
            for ip, n in ip_counts.most_common(50)
        ],
        "top_users": [{"user": u, "count": n} for u, n in user_counts.most_common(20)],
        "top_countries": [{"cc": cc, "count": n} for cc, n in country_counts.most_common(20)],
        "ip_geo": {
            ip: {
                "n": n,
                "lat": cache.get(ip, {}).get("lat"),
                "lon": cache.get(ip, {}).get("lon"),
                "country": cache.get(ip, {}).get("country", "?"),
                "city": cache.get(ip, {}).get("city", ""),
                "org": cache.get(ip, {}).get("org", ""),
            }
            for ip, n in ip_counts.items()
            if cache.get(ip, {}).get("lat") is not None
        },
        "recent": [
            {"ts": e["ts"], "ip": e["ip"], "user": e["user"], "country": cache.get(e["ip"], {}).get("country", "?"), "cc": cache.get(e["ip"], {}).get("cc", "??")}
            for e in events[-200:]
        ],
    }
    OUT.write_text(json.dumps(out))
    print(f"[*] wrote {OUT} ({OUT.stat().st_size} bytes)", file=sys.stderr)


if __name__ == "__main__":
    main()
