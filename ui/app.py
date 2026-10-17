"""Streamlit entrypoint for Cascade dashboard."""

import os
import runpy
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

if "app" in sys.modules and not hasattr(sys.modules["app"], "__path__"):
    del sys.modules["app"]

_DASHBOARD_FILE = os.path.join(os.path.dirname(__file__), "dashboard.py")
runpy.run_path(_DASHBOARD_FILE, run_name="__main__")
