#!/usr/bin/env python3
"""Explicit local source cache, keyed by URL/model/revision/locator. No downloads or model calls."""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import shutil
import sys

from cutaway import atomic_json, digest, load, text_value


def identity(url, model, revision, locator):
    fields = {"url": url, "model": model, "revision": revision, "locator": locator}
    for name, value in fields.items():
        text_value(value, name)
    key = hashlib.sha256(json.dumps(fields, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return key, fields


def get(root, url, model, revision, locator):
    root = Path(root).resolve()
    key, fields = identity(url, model, revision, locator)
    entry = load(root / "entries" / (key + ".json"))
    asset = root / entry["path"]
    if entry["identity"] != fields or digest(asset) != entry["sha256"]:
        raise ValueError("Source cache integrity mismatch; inspect and restore from source")
    return {**entry, "file": str(asset)}


def put(root, file, url, model, revision, locator, applicability):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    with (root / ".cache.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            return _put(root, file, url, model, revision, locator, applicability)
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def _put(root, file, url, model, revision, locator, applicability):
    text_value(applicability, "applicability")
    root = Path(root).resolve()
    key, fields = identity(url, model, revision, locator)
    manifest = root / "entries" / (key + ".json")
    checksum = digest(file)
    if manifest.exists():
        old = get(root, url, model, revision, locator)
        if old["sha256"] != checksum or old["applicability"] != applicability:
            raise ValueError("Cache key already holds a different asset/applicability; record a new revision or locator")
        return old
    destination = root / "assets" / checksum
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and digest(destination) != checksum:
        raise ValueError("Cached asset changed")
    if not destination.exists():
        shutil.copy2(file, destination)
    atomic_json(manifest, {"identity": fields, "sha256": checksum, "path": str(destination.relative_to(root)),
                         "applicability": applicability})
    return get(root, url, model, revision, locator)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("get", "put"))
    for name in ("root", "url", "model", "revision", "locator"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--file"); parser.add_argument("--applicability")
    args = parser.parse_args()
    try:
        if args.command == "get":
            result = get(args.root, args.url, args.model, args.revision, args.locator)
        else:
            if not args.file or not args.applicability:
                raise ValueError("put requires --file and --applicability")
            result = put(args.root, args.file, args.url, args.model, args.revision, args.locator, args.applicability)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
