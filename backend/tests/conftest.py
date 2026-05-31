from pathlib import Path
import shutil
import sys
import uuid

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def workspace_tmp_path() -> Path:
    """
    Provide a per-test temporary directory inside this project.

    This avoids pytest's global tmp_path base directory, which can be fragile on
    Windows when the shared temp folder is locked by another process.
    """

    temp_path = BACKEND_ROOT / ".test_tmp" / uuid.uuid4().hex
    temp_path.mkdir(parents=True)

    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)
