#!/usr/bin/env python3
"""
GuardianVisa — Full System Pre-flight Check
Run: python scripts/validate_all.py
"""

import subprocess
import sys

checks = [
    ("MongoDB Connection", "scripts/validate_mongodb.py"),
    ("GCP / Vertex AI",    "scripts/validate_gcp.py"),
]

overall_exit = 0

for name, script in checks:
    print(f"\n{'='*50}")
    print(f"🔍 Checking: {name}")
    print("=" * 50)
    result = subprocess.run([sys.executable, script], capture_output=False)
    if result.returncode != 0:
        overall_exit = 1

print("\n" + "=" * 50)
print("🚀 Pre-flight complete! Check results above.")
print("=" * 50 + "\n")

sys.exit(overall_exit)
