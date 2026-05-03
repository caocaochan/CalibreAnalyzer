from __future__ import annotations

import datetime as dt
import os
import re
import subprocess
import sys


TAG_RE = re.compile(r"^v(\d{4}\.\d{2}\.\d{2})\.(\d+)$")


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def main():
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y.%m.%d")
    try:
        output = run("git", "tag", "--list", f"v{today}.*")
        tags = [line.strip() for line in output.splitlines() if line.strip()]
    except subprocess.CalledProcessError:
        tags = []

    highest = 0
    for tag in tags:
        match = TAG_RE.match(tag)
        if not match or match.group(1) != today:
            continue
        highest = max(highest, int(match.group(2)))

    version = f"{today}.{highest + 1}"
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as fh:
            fh.write(f"version={version}\n")
            fh.write(f"tag=v{version}\n")

    print(version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
