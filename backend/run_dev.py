"""
Development server runner

Starts the FastAPI server in development mode with auto-reload.
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("Starting Incentive Query API - Development Server")
    print("=" * 70)
    print("\nServer will start at: http://localhost:8000")
    print("API docs available at: http://localhost:8000/docs")
    print("Health check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server\n")
    print("=" * 70)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
