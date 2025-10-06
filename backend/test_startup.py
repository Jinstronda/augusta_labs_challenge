"""
Quick test to verify the FastAPI app can be imported and initialized.

This doesn't start the server, just checks for import errors and basic setup.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("[TEST] Importing FastAPI app...")
    from app.main import app
    
    print("[TEST] ✓ App imported successfully")
    print(f"[TEST] App title: {app.title}")
    print(f"[TEST] App version: {app.version}")
    
    # Check routes
    routes = [route.path for route in app.routes]
    print(f"[TEST] Routes registered: {len(routes)}")
    for route in routes:
        print(f"  - {route}")
    
    print("\n[TEST] ✓ All checks passed!")
    print("[TEST] To start the server, run:")
    print("[TEST]   uvicorn app.main:app --reload")
    
except ImportError as e:
    print(f"[TEST] ✗ Import error: {e}")
    print("[TEST] Make sure to install dependencies:")
    print("[TEST]   pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"[TEST] ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
