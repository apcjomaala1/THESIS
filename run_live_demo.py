"""
Top-level launcher for the WASD Conversation Model Demo.
Run:
    python run_live_demo.py
Then open http://127.0.0.1:5000 in your browser.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEMO_DIR = ROOT / "grooming-detector" / "grooming-detector-trajectory-pipeline" / "demo_live"

sys.path.insert(0, str(DEMO_DIR))

if __name__ == "__main__":
    from app import main
    main()
