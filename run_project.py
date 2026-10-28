import os
import sys
import uvicorn

if __name__ == "__main__":
    # Add backend directory to sys.path
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    sys.path.insert(0, backend_dir)

    print("=" * 65)
    print("  EDUBRIDGE HYBRID LEARNING & STUDENT MANAGEMENT PLATFORM")
    print("=" * 65)
    print("  Platform URL    : http://localhost:8000")
    print("  Interactive Docs: http://localhost:8000/docs")
    print("  Default Admin   : 9876543210 (Password: Admin@123)")
    print("  Default Student : 9876543221 (Password: Student@123)")
    print("=" * 65)

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, app_dir=backend_dir)
