"""Run every validator in this folder. Exit code 0 only when the two checks that gate pass."""
import subprocess
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
status = 0
for script, gates in [("validate_docs.py", True), ("check_cases.py", True), ("probe_untyped.py", False)]:
    print(f"\n===== {script} =====", flush=True)
    code = subprocess.run([sys.executable, str(here / script)], cwd=here).returncode
    if gates and code:
        status = 1
print("\nOVERALL:", "PASS" if status == 0 else "FAIL")
sys.exit(status)
