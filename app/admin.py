from fastapi import APIRouter, Depends
from app.auth import require_role
import time
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Admin"])

# Счётчик запросов (простой, можно расширить)
request_counter = 0
start_time = time.time()

def increment_counter():
    global request_counter
    request_counter += 1

@router.get("/metrics")
async def admin_metrics(_ = Depends(require_role("admin"))):
    uptime_seconds = time.time() - start_time
    return {
        "uptime_seconds": uptime_seconds,
        "uptime_human": str(datetime.utcfromtimestamp(uptime_seconds).strftime("%H:%M:%S")),
        "total_predict_requests": request_counter,
        "version": "1.0.0",
        "status": "healthy"
    }

@router.get("/health")
async def admin_health(_ = Depends(require_role("admin"))):
    # Дополнительная проверка модели и т.п.
    return {"status": "ok", "admin_access": True}