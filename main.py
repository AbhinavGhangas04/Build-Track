import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import (
    auth,
    projects,
    bills,
    labour,
    uploads,
    materials,
    payments,
    contracts,
    notifications,
    ocr,
    reports,
    ai,
    daily_logs,
)
from database import create_tables

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
uploads_dir = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(uploads_dir, exist_ok=True)

app = FastAPI(title="BuildTrack Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(bills.router, prefix="/api/bills", tags=["Bills"])
app.include_router(labour.router, prefix="/api/labour", tags=["Labour"])
app.include_router(materials.router, prefix="/api/materials", tags=["Materials"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(contracts.router, prefix="/api/contracts", tags=["Contracts"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Features"])
app.include_router(daily_logs.router, prefix="/api/daily-logs", tags=["Daily Logs"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["Uploads"])

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

@app.on_event("startup")
async def startup():
    try:
        await create_tables()
    except Exception as e:
        print(f"DB init warning: {e}")