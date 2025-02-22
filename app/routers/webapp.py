from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

router = APIRouter()

# Путь к статическим файлам
static_path = Path(__file__).parent.parent / "static" / "webapp"

# Монтируем статические файлы
router.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@router.get("/webapp")
async def get_webapp():
    """Возвращает HTML страницу веб-приложения"""
    index_path = static_path / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Web App not found")
    return FileResponse(index_path) 