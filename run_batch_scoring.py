"""
Wrapper script to run batch processing from root directory.
This ensures config.env is loaded correctly.
"""
import sys
import os

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import and run
from scripts.batch_process_with_scoring import main

if __name__ == "__main__":
    main()
