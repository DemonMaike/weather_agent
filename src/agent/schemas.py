from pydantic import BaseModel, Field
from typing import Optional, Any

class GeocodeRequest(BaseModel):
    city: str = Field(..., description="Название города")

class WeatherRequest(BaseModel):
    lat: float = Field(..., description="Широта")
    lon: float = Field(..., description="Долгота")
    forecast_days: int = Field(default=1, ge=1, le=16, description="Количество дней прогноза")
    include_current: bool = Field(default=True, description="Включить текущую погоду")

class MCPToolCall(BaseModel):
    tool_name: str
    arguments: dict[str, Any]

class MCPResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None