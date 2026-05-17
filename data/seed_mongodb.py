# Usage: python seed_mongodb.py
# Drops and recreates all GuardianVisa collections, then inserts seed data.
# Requires MONGODB_URI to be set in the environment (or a .env file in the project root).

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    print("❌  MONGODB_URI is not set. Add it to your .env file or export it.", file=sys.stderr)
    sys.exit(1)

SEED_FILES = {
    "students":           "seed_students.json",
    "visa_rules":         "seed_visa_rules.json",
    "scam_patterns":      "seed_scam_patterns.json",
    "emergency_resources":"seed_emergency_resources.json",
}

SEED_DIR = Path(__file__).parent


def seed_collection(db, collection_name: str, filename: str) -> None:
    filepath = SEED_DIR / filename
    if not filepath.exists():
        print(f"⚠️  Seed file not found, skipping: {filepath}")
        return

    with filepath.open("r", encoding="utf-8") as f:
        documents = json.load(f)

    if not isinstance(documents, list):
        documents = [documents]

    collection = db[collection_name]
    collection.drop()
    result = collection.insert_many(documents)
    print(f"✅  Seeded {len(result.inserted_ids)} documents into collection '{collection_name}'")


def main() -> None:
    print("🔗  Connecting to MongoDB …")
    client = MongoClient(MONGODB_URI)

    db_name = "guardianvisa"
    db = client[db_name]
    print(f"📦  Using database: {db_name}\n")

    for collection_name, filename in SEED_FILES.items():
        seed_collection(db, collection_name, filename)

    client.close()
    print("\n🎉  All collections seeded successfully.")


if __name__ == "__main__":
    main()
