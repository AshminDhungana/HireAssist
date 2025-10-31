import os
import subprocess
import sys
import pytest


RUN_INTEGRATION = os.environ.get("RUN_INTEGRATION_TESTS") == "1"


@pytest.mark.skipif(not RUN_INTEGRATION, reason="Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable")
def test_run_parse_script_runs_and_exits_zero():
    """Optional integration: runs the script against the real DB configured in env.

    This is skipped by default; CI can enable it by setting RUN_INTEGRATION_TESTS=1 and
    providing DATABASE_URL in the environment.
    """
    base = os.path.dirname(os.path.dirname(__file__))
    script = os.path.join(base, "scripts", "run_parse_test.py")
    assert os.path.exists(script), "run_parse_test.py missing"

    # Use the venv-provided python if available in PATH; rely on environment in CI
    python = sys.executable
    proc = subprocess.run([python, script], capture_output=True, text=True)
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0
