"""Pydantic-схемы для API."""
from pydantic import BaseModel, Field
from typing import List


class GenerateRequest(BaseModel):
    """Запрос на генерацию сада."""
    groups: List[int] = Field(
        ..., min_length=1, max_length=10,
        description="Количество камней в каждой группе",
        examples=[[5, 2, 3, 2, 3]]
    )
    show_golden_grid: bool = Field(
        default=False,
        description="Показывать ли золотую сетку"
    )
    seed: int = Field(
        default=42,
        description="Зерно случайности для воспроизводимости"
    )


class StoneOut(BaseModel):
    """Один камень."""
    x: float
    y: float
    radius: float
    group: int


class GardenResponse(BaseModel):
    """Ответ с координатами камней и метаданными."""
    stones: List[StoneOut]
    width: float
    height: float
    total: int
    status: str
    message: str
    suggestions: List[str]
    golden_ratio: float = 1.6180339887


class VariantsRequest(BaseModel):
    """Запрос вариантов разбиения."""
    total: int = Field(..., ge=3, le=40)


class VariantItem(BaseModel):
    name: str
    groups: List[int]


class VariantsResponse(BaseModel):
    total: int
    variants: List[VariantItem]


class PresetOut(BaseModel):
    id: str
    name: str
    description: str
    groups: List[int]
    emoji: str