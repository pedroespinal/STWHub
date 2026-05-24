#!/usr/bin/env python3
"""
GitHub Actions script — processes a [COMMUNITY BUILD] issue and adds
the build to community_builds.json, then commits and closes the issue.

Env vars provided by the workflow:
  ISSUE_BODY   — raw issue body text
  ISSUE_NUMBER — issue number (int as string)
  ISSUE_TITLE  — issue title
  GH_TOKEN     — GITHUB_TOKEN (auto, has contents:write + issues:write)
  REPO         — "owner/repo"
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── Helpers ───────────────────────────────────────────────────────────────────

def gh_api(method: str, path: str, body: dict | None = None):
    token = os.environ["GH_TOKEN"]
    repo  = os.environ["REPO"]
    url   = f"https://api.github.com/repos/{repo}{path}"
    data  = json.dumps(body).encode() if body else None
    req   = urllib.request.Request(
        url, data=data, method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept":        "application/vnd.github+json",
            "Content-Type":  "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"GitHub API error {e.code}: {e.read().decode()}")
        return None


def close_issue(number: int, comment: str):
    gh_api("POST", f"/issues/{number}/comments", {"body": comment})
    gh_api("PATCH", f"/issues/{number}", {"state": "closed",
                                          "labels": ["community-build"]})


def git(*args):
    result = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    if result.returncode != 0:
        print(f"git {' '.join(args)} failed:\n{result.stderr}")
    return result.returncode == 0


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    issue_body   = os.environ.get("ISSUE_BODY", "")
    issue_number = int(os.environ.get("ISSUE_NUMBER", "0"))
    repo         = os.environ.get("REPO", "")

    # ── 1. Extract JSON block from issue body ─────────────────────────────────
    match = re.search(r"```json\s*(\{.*?\})\s*```", issue_body, re.DOTALL)
    if not match:
        close_issue(issue_number,
            "❌ **No se encontró JSON válido en el cuerpo del issue.**\n"
            "Por favor re-envía desde STW Hub.")
        sys.exit(0)

    try:
        build = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        close_issue(issue_number,
            f"❌ **JSON inválido:** `{e}`\nPor favor re-envía desde STW Hub.")
        sys.exit(0)

    # ── 2. Validate required fields ───────────────────────────────────────────
    required = ["name", "cls", "hero"]
    missing  = [f for f in required if not build.get(f)]
    if missing:
        close_issue(issue_number,
            f"❌ **Faltan campos obligatorios:** {', '.join(missing)}")
        sys.exit(0)

    # ── 3. Load existing community_builds.json ────────────────────────────────
    builds_path = Path("community_builds.json")
    try:
        existing = json.loads(builds_path.read_text(encoding="utf-8"))
    except Exception:
        existing = []

    # ── 4. Duplicate check (same name + class) ─────────────────────────────────
    new_key = f"{build.get('name','').lower()}_{build.get('cls','').lower()}"
    for b in existing:
        key = f"{b.get('name','').lower()}_{b.get('cls','').lower()}"
        if key == new_key:
            close_issue(issue_number,
                f"⚠️ Ya existe una build de comunidad con el mismo nombre y clase: "
                f"**{build.get('name')} ({build.get('cls')})**.\n"
                "Si es una versión mejorada, edita la existente.")
            sys.exit(0)

    # ── 5. Assign a proper unique ID ──────────────────────────────────────────
    today  = datetime.now(timezone.utc).strftime("%Y%m%d")
    max_n  = max(
        (int(b["id"].split("_")[-1]) for b in existing
         if b.get("id", "").startswith("community_") and
            b["id"].split("_")[-1].isdigit()),
        default=0
    )
    build["id"] = f"community_{today}_{max_n + 1:04d}"

    # ── 6. Normalise bilingual fields ─────────────────────────────────────────
    # If only one language was provided, mirror it to the other
    for pair in [("desc_es", "desc_en"), ("purpose_es", "purpose_en"),
                 ("support_es", "support_en"), ("gadgets_es", "gadgets_en"),
                 ("team_perk_es", "team_perk_en")]:
        a, b_key = pair
        if build.get(a) and not build.get(b_key):
            build[b_key] = build[a]
        elif build.get(b_key) and not build.get(a):
            build[a] = build[b_key]

    build["votes"]  = 0
    build["author"] = build.get("author") or "Community"

    # ── 7. Append + save ──────────────────────────────────────────────────────
    existing.append(build)
    builds_path.write_text(
        json.dumps(existing, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # ── 8. Git commit + push ──────────────────────────────────────────────────
    git("config", "user.name",  "STW Hub Bot")
    git("config", "user.email", "bot@stwhub.app")
    git("add", "community_builds.json")
    git("commit", "-m",
        f"feat: add community build '{build['name']}' ({build['cls']}) "
        f"[issue #{issue_number}]")
    git("push")

    # ── 9. Close issue with success message ───────────────────────────────────
    close_issue(issue_number,
        f"✅ **¡Build añadido a la comunidad!**\n\n"
        f"**{build['name']}** ({build['cls']}) — ID: `{build['id']}`\n\n"
        f"Los usuarios verán este build la próxima vez que abran STW Hub.\n\n"
        f"_Procesado automáticamente por STW Hub Bot_"
    )

    print(f"✅ Build '{build['name']}' added successfully with ID {build['id']}")


if __name__ == "__main__":
    main()
