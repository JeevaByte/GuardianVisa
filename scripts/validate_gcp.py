#!/usr/bin/env python3
"""
GuardianVisa — GCP / Vertex AI Connection Validator
Run: python scripts/validate_gcp.py
"""

import os
import sys
from pathlib import Path

# ── ANSI colour helpers ───────────────────────────────────────────────────────
GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"

def ok(msg: str)   -> None: print(f"  {GREEN}✔ PASS{RESET}  {msg}")
def fail(msg: str) -> None: print(f"  {RED}✘ FAIL{RESET}  {msg}")


# ── Load backend/.env ─────────────────────────────────────────────────────────
def load_env() -> dict[str, str]:
    env_path = Path(__file__).parent.parent / "backend" / ".env"
    env: dict[str, str] = {}
    if not env_path.exists():
        return env
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


def main() -> None:
    passed = 0
    failed = 0

    print("\n" + "=" * 50)
    print("  GCP / Vertex AI — Pre-flight Check")
    print("=" * 50)

    env = load_env()
    # Merge into os.environ so SDK picks up the values automatically
    for key, value in env.items():
        os.environ.setdefault(key, value)

    project_id  = os.environ.get("GCP_PROJECT_ID", "")
    location    = os.environ.get("GCP_LOCATION", "us-central1")
    model_name  = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")
    agent_id    = os.environ.get("AGENT_ID", "")
    creds_file  = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")

    # ── Check 1: GCP_PROJECT_ID ───────────────────────────────────────────────
    if project_id:
        ok(f"GCP_PROJECT_ID = {project_id}")
        passed += 1
    else:
        fail("GCP_PROJECT_ID is not set in backend/.env")
        failed += 1

    # ── Check 2: Credentials file ─────────────────────────────────────────────
    if creds_file:
        creds_path = Path(creds_file)
        if not creds_path.is_absolute():
            creds_path = Path(__file__).parent.parent / "backend" / creds_file
        if creds_path.exists():
            ok(f"Credentials file found: {creds_path}")
            passed += 1
        else:
            fail(f"Credentials file NOT found: {creds_path}")
            failed += 1
    else:
        fail("GOOGLE_APPLICATION_CREDENTIALS is not set in backend/.env")
        failed += 1

    # ── Check 3: vertexai import & init ───────────────────────────────────────
    try:
        import vertexai  # type: ignore
        vertexai.init(project=project_id, location=location)
        ok(f"vertexai.init() succeeded (project={project_id}, location={location})")
        passed += 1
    except ImportError:
        fail("vertexai package not installed — run: pip install google-cloud-aiplatform")
        failed += 1
        print("\n" + "=" * 50)
        print(f"  {RED}❌ GCP setup incomplete{RESET}  ({passed} passed, {failed} failed)")
        print("=" * 50 + "\n")
        sys.exit(1)
    except Exception as exc:
        fail(f"vertexai.init() failed: {exc}")
        failed += 1

    # ── Check 4: Gemini generate_content ─────────────────────────────────────
    try:
        from vertexai.generative_models import GenerativeModel  # type: ignore
        model    = GenerativeModel(model_name)
        response = model.generate_content("Say hello in one word")
        text     = response.text.strip()
        ok(f"Gemini ({model_name}) responded: {text!r}")
        passed += 1
    except Exception as exc:
        fail(f"Gemini call failed: {exc}")
        failed += 1

    # ── Check 5: AGENT_ID ─────────────────────────────────────────────────────
    if agent_id:
        ok(f"AGENT_ID = {agent_id}")
        passed += 1
    else:
        fail("AGENT_ID is not set in backend/.env (required for Vertex AI Agent Builder)")
        failed += 1

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    if failed == 0:
        print(f"  {GREEN}✅ GCP ready!{RESET}  All {passed} checks passed.")
    else:
        print(f"  {RED}❌ GCP setup incomplete{RESET}  ({passed} passed, {failed} failed)")
    print("=" * 50 + "\n")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
