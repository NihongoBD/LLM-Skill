#!/usr/bin/env python3
"""
Check live registry data for packages and recommend a safe version to pin.

For each package it reports the newest stable release, how old it is, and the
recommended version: the newest stable, non-deprecated release that is at least
--min-age-days old (default 14). Freshly published releases are where broken or
malicious versions are most often caught, so they are skipped on purpose.

A package that does not exist is reported as NOT FOUND. Treat that as a red
flag: the name may be a typo, a look-alike, or invented.

Usage:
  python check_versions.py next react @nestjs/core prisma
  python check_versions.py --pypi django djangorestframework
  python check_versions.py --min-age-days 30 --json vitest

Only the Python standard library is used.
"""
import argparse
import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

NPM_REGISTRY = "https://registry.npmjs.org/"
NPM_DOWNLOADS = "https://api.npmjs.org/downloads/point/last-week/"
PYPI = "https://pypi.org/pypi/{}/json"
TIMEOUT = 90
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$")
PY_PRE = re.compile(r"(a|b|rc|alpha|beta|pre|preview|dev)\d*", re.IGNORECASE)


def fetch_json(url, accept="application/json"):
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "automation-version-check"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_time(value):
    if not value:
        return None
    value = value.replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed


def age_days(when, now):
    return None if when is None else (now - when).days


def semver_key(version):
    m = SEMVER.match(version)
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def py_key(version):
    parts = re.findall(r"\d+", version.split("+")[0])
    return tuple(int(p) for p in parts[:4]) if parts else None


def check_npm(name, min_age, now):
    encoded = urllib.parse.quote(name, safe="@")
    try:
        doc = fetch_json(NPM_REGISTRY + encoded)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return {"package": name, "status": "NOT FOUND", "note": "No such package on npm. Check the spelling; it may be a look-alike or invented name."}
        return {"package": name, "status": "ERROR", "note": f"HTTP {err.code}"}
    except Exception as err:  # network problems
        return {"package": name, "status": "ERROR", "note": str(err)}

    times = doc.get("time", {})
    versions = doc.get("versions", {})
    latest_tag = doc.get("dist-tags", {}).get("latest")
    stable = []
    for version, manifest in versions.items():
        m = SEMVER.match(version)
        if not m or m.group(4):  # skip unparseable and pre-release
            continue
        if isinstance(manifest, dict) and manifest.get("deprecated"):
            continue
        stable.append((semver_key(version), version, parse_time(times.get(version))))
    stable.sort(key=lambda item: item[0])

    result = {
        "package": name,
        "registry": "npm",
        "latest_tag": latest_tag,
        "latest_tag_is_prerelease": bool(latest_tag and "-" in latest_tag),
        "license": doc.get("license") if isinstance(doc.get("license"), str) else None,
        "repository": (doc.get("repository") or {}).get("url") if isinstance(doc.get("repository"), dict) else doc.get("repository"),
        "last_publish": times.get("modified"),
    }
    if latest_tag and isinstance(versions.get(latest_tag), dict) and versions[latest_tag].get("deprecated"):
        result["deprecated"] = versions[latest_tag]["deprecated"]
    return finish(result, stable, min_age, now, weekly_downloads(encoded))


def weekly_downloads(encoded):
    try:
        return fetch_json(NPM_DOWNLOADS + encoded).get("downloads")
    except Exception:
        return None


def check_pypi(name, min_age, now):
    try:
        doc = fetch_json(PYPI.format(urllib.parse.quote(name)))
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return {"package": name, "status": "NOT FOUND", "note": "No such package on PyPI. Check the spelling; it may be a look-alike or invented name."}
        return {"package": name, "status": "ERROR", "note": f"HTTP {err.code}"}
    except Exception as err:
        return {"package": name, "status": "ERROR", "note": str(err)}

    stable = []
    for version, files in doc.get("releases", {}).items():
        if PY_PRE.search(version) or not files:
            continue
        if all(f.get("yanked") for f in files):
            continue
        uploaded = min((parse_time(f.get("upload_time_iso_8601")) for f in files if f.get("upload_time_iso_8601")), default=None)
        key = py_key(version)
        if key:
            stable.append((key, version, uploaded))
    stable.sort(key=lambda item: item[0])
    info = doc.get("info", {})
    result = {
        "package": name,
        "registry": "pypi",
        "latest_tag": info.get("version"),
        "latest_tag_is_prerelease": bool(PY_PRE.search(info.get("version") or "")),
        "license": info.get("license") or None,
        "repository": (info.get("project_urls") or {}).get("Source") or info.get("home_page"),
    }
    return finish(result, stable, min_age, now, None)


def finish(result, stable, min_age, now, downloads):
    result["weekly_downloads"] = downloads
    if not stable:
        result.update(status="NO STABLE RELEASE", note="Only pre-releases or deprecated versions exist. Avoid unless there is a strong reason.")
        return result
    newest = stable[-1]
    old_enough = [item for item in stable if item[2] is not None and age_days(item[2], now) >= min_age]
    result["newest_stable"] = newest[1]
    result["newest_stable_age_days"] = age_days(newest[2], now)
    notes = []
    if old_enough:
        rec = old_enough[-1]
        result["recommended"] = rec[1]
        result["recommended_age_days"] = age_days(rec[2], now)
        if rec[1] != newest[1]:
            notes.append(f"newest stable {newest[1]} is younger than {min_age} days; pinning {rec[1]}")
        if rec[0][0] != newest[0][0]:
            notes.append("recommended version is a different MAJOR than the newest; re-check in a few days or read the changelog")
    else:
        result["recommended"] = None
        notes.append(f"no stable release is {min_age}+ days old yet")
    if result.get("latest_tag_is_prerelease"):
        notes.append("the 'latest' tag points to a pre-release; ignored")
    if result.get("deprecated"):
        notes.append("latest is deprecated: " + str(result["deprecated"])[:120])
    newest_age = result.get("newest_stable_age_days")
    if newest_age is not None and newest_age > 365:
        notes.append("no stable release in over a year; check the project is maintained")
    if downloads is not None and downloads < 1000:
        notes.append("fewer than 1,000 weekly downloads; confirm this is the official package")
    result["status"] = "OK" if result["recommended"] else "WAIT"
    result["note"] = "; ".join(notes)
    return result


def print_table(rows):
    headers = ["package", "status", "recommended", "age(d)", "newest stable", "weekly dl", "note"]
    data = []
    for r in rows:
        data.append([
            r["package"], r.get("status", ""), r.get("recommended") or "-",
            str(r.get("recommended_age_days", "-")), r.get("newest_stable") or "-",
            f"{r['weekly_downloads']:,}" if isinstance(r.get("weekly_downloads"), int) else "n/a",
            r.get("note", ""),
        ])
    widths = [max(len(str(x)) for x in col) for col in zip(headers, *data)]
    widths[-1] = min(widths[-1], 90)
    line = "  ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(line)
    print("-" * len(line))
    for row in data:
        print("  ".join(str(c)[:w].ljust(w) if i == len(row) - 1 else str(c).ljust(w) for i, (c, w) in enumerate(zip(row, widths))))
    for r in rows:
        if r.get("repository"):
            print(f"  repo {r['package']}: {r['repository']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("packages", nargs="+")
    parser.add_argument("--pypi", action="store_true", help="look packages up on PyPI instead of npm")
    parser.add_argument("--min-age-days", type=int, default=14)
    parser.add_argument("--json", action="store_true", help="print JSON instead of a table")
    args = parser.parse_args()

    now = dt.datetime.now(dt.timezone.utc)
    check = check_pypi if args.pypi else check_npm
    rows = [check(p, args.min_age_days, now) for p in args.packages]
    if args.json:
        print(json.dumps(rows, indent=2, default=str))
    else:
        print_table(rows)
    bad = [r for r in rows if r.get("status") in {"NOT FOUND", "ERROR", "NO STABLE RELEASE"}]
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
