"""FastAPI-сервер: точка входа для API генератора сада."""
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from garden.validator import validate_group_input, auto_suggest_from_single
from garden.generator import create_garden
from garden.math_core import PHI

from .schemas import (
    GenerateRequest, GardenResponse, StoneOut,
    VariantsRequest, VariantsResponse, VariantItem,
    PresetOut,
)
from .render import render_garden_png


# ---------- ПРИЛОЖЕНИЕ ----------
app = FastAPI(
    title="JapGarden API",
    description="Генератор сада Рёандзи по числам Фибоначчи и золотому сечению",
    version="1.0.0",
)

# CORS — чтобы веб-страница и Android могли обращаться
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # для продакшена сузить!
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- ПРЕСЕТЫ ----------
PRESETS_DIR = Path(__file__).resolve().parent.parent / "presets"


def _load_presets():
    """Загружает все .json из папки presets."""
    presets = []
    if not PRESETS_DIR.exists():
        return presets
    for path in sorted(PRESETS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["id"] = path.stem
            presets.append(data)
        except Exception as e:
            print(f"⚠️ Не удалось загрузить пресет {path.name}: {e}")
    return presets


# ---------- ЭНДПОИНТЫ ----------

@app.get("/")
def root():
    """Информация о сервере."""
    return {
        "name": "JapGarden API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "GET  /api/presets",
            "POST /api/variants",
            "POST /api/analyze",
            "POST /api/generate       (JSON с координатами)",
            "POST /api/render         (PNG-изображение)",
        ],
    }


@app.get("/api/health")
def health():
    """Проверка, что сервер жив."""
    return {"status": "ok", "phi": PHI}


@app.get("/api/presets", response_model=list[PresetOut])
def get_presets():
    """Возвращает список классических пресетов."""
    return _load_presets()


@app.post("/api/variants", response_model=VariantsResponse)
def post_variants(req: VariantsRequest):
    """Возвращает варианты разбиения N камней."""
    variants = auto_suggest_from_single(req.total)
    if not variants:
        raise HTTPException(
            status_code=400,
            detail=f"Не могу предложить разбиение для {req.total} камней"
        )
    return VariantsResponse(
        total=req.total,
        variants=[VariantItem(name=n, groups=g) for n, g in variants]
    )


@app.post("/api/analyze")
def post_analyze(req: GenerateRequest):
    """Только валидация, без генерации."""
    status, message, suggestions = validate_group_input(req.groups)
    return {
        "status": status,
        "message": message,
        "suggestions": suggestions,
        "total": sum(req.groups),
        "groups": req.groups,
    }


@app.post("/api/generate", response_model=GardenResponse)
def post_generate(req: GenerateRequest):
    """
    Генерирует координаты камней и возвращает JSON.
    Используется Kotlin-приложением для нативной отрисовки.
    """
    status, message, suggestions = validate_group_input(req.groups)
    if status == "error":
        raise HTTPException(status_code=400, detail=message)

    stones, w, h = create_garden(req.groups)
    return GardenResponse(
        stones=[StoneOut(**s) for s in stones],
        width=w,
        height=h,
        total=sum(req.groups),
        status=status,
        message=message,
        suggestions=suggestions,
    )


@app.post("/api/render")
def post_render(req: GenerateRequest):
    """
    Генерирует сад и возвращает PNG-изображение.
    Используется веб-страницей напрямую.
    """
    status, message, _ = validate_group_input(req.groups)
    if status == "error":
        raise HTTPException(status_code=400, detail=message)

    stones, w, h = create_garden(req.groups)
    png_bytes = render_garden_png(
        stones, w, h,
        show_golden_grid=req.show_golden_grid
    )
    return Response(content=png_bytes, media_type="image/png")


# ---------- СТАТИЧЕСКИЕ ФАЙЛЫ (веб-фронтенд) ----------
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
if WEB_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(WEB_DIR), html=True),
              name="web")