"""
Pytest configuration: adds the package root to sys.path so tests can import
the pipeline modules without an editable install.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
