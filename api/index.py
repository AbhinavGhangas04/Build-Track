import os, sys
# Add the project root to PYTHONPATH so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the FastAPI `app` defined in `main.py`
from main import app  # noqa: F401