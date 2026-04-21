#!/usr/bin/env python
"""Run the Core Chat Engine backend server."""

import uvicorn
import os
import sys

# Add the backend directory to the path so imports work
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Change to backend directory so src/ is found correctly
os.chdir(script_dir)

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=True,
    )
