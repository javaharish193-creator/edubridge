from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config import settings
from app.database import engine, Base
from app.models import *  # Ensure all models are imported for Base.metadata.create_all
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.content import router as content_router
from app.api.assignments import router as assignments_router
from app.api.live import router as live_router
from app.api.student import router as student_router
from app.api.files import router as files_router
from app.api.ai import router as ai_router

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Standardized Error Handling (Specification page 13)
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        code = detail.get("code", "ERROR")
        message = detail.get("message", str(detail))
        details = detail.get("details", None)
    else:
        code = "HTTP_ERROR"
        message = str(detail)
        details = None

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = err.get("loc", [])
        field_name = loc[-1] if loc else "unknown"
        errors.append({"field": str(field_name), "issue": err.get("msg", "Invalid value")})
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed",
                "details": errors
            }
        }
    )

# Include API Routers under /api/v1
v1_prefix = settings.API_V1_PREFIX
app.include_router(auth_router, prefix=v1_prefix)
app.include_router(admin_router, prefix=v1_prefix)
app.include_router(content_router, prefix=v1_prefix)
app.include_router(assignments_router, prefix=v1_prefix)
app.include_router(live_router, prefix=v1_prefix)
app.include_router(student_router, prefix=v1_prefix)
app.include_router(files_router, prefix=v1_prefix)
app.include_router(ai_router, prefix=v1_prefix)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Static files & frontend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "service": "EduBridge API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "ok"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
