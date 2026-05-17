#!/usr/bin/env python3
"""
GuardianVisa — MongoDB Connection Validator
Run: python scripts/validate_mongodb.py
"""

import sys
from pathlib import Path

# Resolve backend/.env relative to this script's location
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR.parent / "backend" / ".env"

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

PASS = f"{GREEN}PASS{RESET}"
FAIL = f"{RED}FAIL{RESET}"

EXPECTED_COUNTS = {
    "students": 3,
    "visa_rules": 4,
    "scam_patterns": 8,
    "emergency_resources": 18,
}

failures = 0


def check(label: str, passed: bool, detail: str = "") -> None:
    global failures
    status = PASS if passed else FAIL
    msg = f"[{status}] {label}"
    if detail:
        msg += f"  ({detail})"
    print(msg)
    if not passed:
        failures += 1


def main() -> None:
    # ── Load .env ────────────────────────────────────────────────────────────
    try:
        from dotenv import load_dotenv
    except ImportError:
        print(f"{RED}ERROR:{RESET} python-dotenv not installed. Run: pip install python-dotenv")
        sys.exit(1)

    if not ENV_PATH.exists():
        print(f"{RED}ERROR:{RESET} .env file not found at {ENV_PATH}")
        print("Create backend/.env with MONGODB_URI=<your-uri>")
        sys.exit(1)

    load_dotenv(ENV_PATH)

    import os
    uri = os.getenv("MONGODB_URI")
    check("MONGODB_URI present in backend/.env", bool(uri))
    if not uri:
        print(f"\n{RED}❌ Cannot proceed without MONGODB_URI.{RESET}")
        sys.exit(1)

    # ── Connect ───────────────────────────────────────────────────────────────
    try:
        from pymongo import MongoClient
        from pymongo.errors import ConnectionFailure, OperationFailure
    except ImportError:
        print(f"{RED}ERROR:{RESET} pymongo not installed. Run: pip install pymongo")
        sys.exit(1)

    client = MongoClient(uri, serverSelectionTimeoutMS=8000)

    # ── Ping ──────────────────────────────────────────────────────────────────
    try:
        client.admin.command("ping")
        check("Connection to MongoDB Atlas", True)
    except ConnectionFailure as exc:
        check("Connection to MongoDB Atlas", False, str(exc))
        print(f"\n{RED}❌ Cannot reach MongoDB Atlas. Check Network Access whitelist.{RESET}")
        sys.exit(1)
    except OperationFailure as exc:
        check("Connection to MongoDB Atlas", False, str(exc))
        print(f"\n{RED}❌ Authentication failed. Check username/password in URI.{RESET}")
        sys.exit(1)

    # ── Database existence ────────────────────────────────────────────────────
    db_names = client.list_database_names()
    db_exists = "guardianvisa" in db_names
    check('Database "guardianvisa" exists', db_exists)
    if not db_exists:
        print(f"  Tip: ensure the URI ends with /guardianvisa and the database has been seeded.")

    db = client["guardianvisa"]

    # ── Collection counts ─────────────────────────────────────────────────────
    print()
    existing_collections = db.list_collection_names()
    for collection_name, min_docs in EXPECTED_COUNTS.items():
        col_exists = collection_name in existing_collections
        if not col_exists:
            check(f"Collection '{collection_name}' exists", False, "collection missing")
            continue

        count = db[collection_name].count_documents({})
        ok = count >= min_docs
        check(
            f"Collection '{collection_name}' has >= {min_docs} docs",
            ok,
            f"found {count}",
        )

    # ── Spot-check a specific document ───────────────────────────────────────
    print()
    student = db["students"].find_one({"_id": "priya_sharma_001"})
    if student:
        name = student.get("name", "<no name field>")
        hours = student.get("work_hours_this_week", "<no field>")
        check("Student 'priya_sharma_001' found", True)
        print(f"    name                 : {name}")
        print(f"    work_hours_this_week : {hours}")
    else:
        check("Student 'priya_sharma_001' found", False, "document not found")

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    if failures == 0:
        print(f"{GREEN}✅ MongoDB ready for GuardianVisa!{RESET}")
    else:
        print(f"{RED}❌ {failures} check{'s' if failures != 1 else ''} failed. See above.{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
