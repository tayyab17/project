"""
Full automation script for Viraj Junction website.

Workflow:
  1. Detect changed files via git
  2. Create a new feature branch
  3. Commit and push changes
  4. Open a Pull Request via GitHub API
  5. Optionally auto-merge after CI passes

Usage:
  python automate.py                        # auto-detect changed files
  python automate.py --message "fix nav"    # custom commit message
  python automate.py --auto-merge           # merge PR automatically after CI

Required environment variables:
  GITHUB_TOKEN   Personal access token with repo + workflow scopes
  GITHUB_OWNER   Repository owner  (e.g. tayyab17)
  GITHUB_REPO    Repository name   (e.g. project)
"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime

import requests

# ── Config ────────────────────────────────────────────────────────────────────

GITHUB_API = "https://api.github.com"
BASE_BRANCH = "main"


def env(key: str) -> str:
    value = os.environ.get(key, "")
    if not value:
        print(f"ERROR: environment variable '{key}' is not set.")
        sys.exit(1)
    return value


# ── Git helpers ───────────────────────────────────────────────────────────────

def run(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"ERROR running: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result


def changed_files() -> list[str]:
    result = run("git status --porcelain")
    files = [line[3:].strip() for line in result.stdout.splitlines() if line.strip()]
    return files


def current_branch() -> str:
    return run("git branch --show-current").stdout.strip()


def branch_exists_remote(branch: str, owner: str, repo: str, token: str) -> bool:
    resp = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/branches/{branch}",
        headers=auth_headers(token),
    )
    return resp.status_code == 200


def auth_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


# ── Core steps ────────────────────────────────────────────────────────────────

def ensure_on_base_branch():
    branch = current_branch()
    if branch != BASE_BRANCH:
        print(f"  Switching from '{branch}' to '{BASE_BRANCH}'...")
        run(f"git checkout {BASE_BRANCH}")
        run(f"git pull origin {BASE_BRANCH}")


def create_feature_branch() -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    branch = f"feature/auto-update-{timestamp}"
    run(f"git checkout -b {branch}")
    print(f"  Created branch: {branch}")
    return branch


def commit_and_push(branch: str, message: str):
    run("git add -A")
    run(f'git commit -m "{message}"')
    run(f"git push -u origin {branch}")
    print(f"  Pushed to origin/{branch}")


def open_pull_request(branch: str, message: str, owner: str, repo: str, token: str) -> dict:
    payload = {
        "title": message,
        "head": branch,
        "base": BASE_BRANCH,
        "body": (
            "## Automated PR\n\n"
            f"Changes detected and committed automatically.\n\n"
            f"**Branch:** `{branch}`  \n"
            f"**Base:** `{BASE_BRANCH}`  \n\n"
            "### Changed files\n"
            + "\n".join(f"- `{f}`" for f in changed_files() or ["(see diff)"])
            + "\n\n---\n_Created by automate.py_"
        ),
    }
    resp = requests.post(
        f"{GITHUB_API}/repos/{owner}/{repo}/pulls",
        headers=auth_headers(token),
        json=payload,
    )
    if resp.status_code not in (200, 201):
        print(f"ERROR creating PR: {resp.status_code} — {resp.text}")
        sys.exit(1)
    pr = resp.json()
    print(f"  PR opened: {pr['html_url']}")
    return pr


def wait_for_checks(pr_number: int, owner: str, repo: str, token: str, timeout: int = 300):
    print(f"  Waiting for CI checks on PR #{pr_number}...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = requests.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}",
            headers=auth_headers(token),
        )
        pr = resp.json()
        mergeable = pr.get("mergeable_state")
        print(f"    mergeable_state = {mergeable}")
        if mergeable == "clean":
            return True
        if mergeable in ("dirty", "blocked"):
            print("  Checks failed or conflicts detected — skipping auto-merge.")
            return False
        time.sleep(15)
    print("  Timed out waiting for checks.")
    return False


def auto_merge(pr_number: int, owner: str, repo: str, token: str):
    resp = requests.put(
        f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}/merge",
        headers=auth_headers(token),
        json={"merge_method": "squash"},
    )
    if resp.status_code == 200:
        print(f"  PR #{pr_number} merged to {BASE_BRANCH}.")
    else:
        print(f"  Could not merge: {resp.status_code} — {resp.text}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Automate git branch → PR → deploy")
    parser.add_argument("--message", "-m", default="", help="Commit / PR title")
    parser.add_argument("--auto-merge", action="store_true", help="Merge PR after CI passes")
    args = parser.parse_args()

    token = env("GITHUB_TOKEN")
    owner = env("GITHUB_OWNER")
    repo  = env("GITHUB_REPO")

    print("\n── Step 1: Check for changes ──────────────────────────────")
    files = changed_files()
    if not files:
        print("  No changes detected. Nothing to do.")
        sys.exit(0)
    print(f"  {len(files)} file(s) changed:")
    for f in files:
        print(f"    • {f}")

    message = args.message or f"chore: auto-update {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    print("\n── Step 2: Create feature branch ──────────────────────────")
    ensure_on_base_branch()
    branch = create_feature_branch()

    print("\n── Step 3: Commit & push ───────────────────────────────────")
    commit_and_push(branch, message)

    print("\n── Step 4: Open Pull Request ───────────────────────────────")
    pr = open_pull_request(branch, message, owner, repo, token)

    if args.auto_merge:
        print("\n── Step 5: Wait for CI & auto-merge ────────────────────────")
        if wait_for_checks(pr["number"], owner, repo, token):
            auto_merge(pr["number"], owner, repo, token)
        else:
            print(f"  PR left open for manual review: {pr['html_url']}")
    else:
        print(f"\nDone. Review and merge the PR at:\n  {pr['html_url']}")


if __name__ == "__main__":
    main()
