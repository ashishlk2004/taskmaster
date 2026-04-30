from datetime import datetime, date
from pydantic import BaseModel


# --- Categories ---

class CategoryCreate(BaseModel):
    name: str
    color: str = "#6366f1"


class CategoryResponse(BaseModel):
    id: int
    name: str
    color: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Tasks ---

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: int = 2
    category_id: int | None = None
    due_date: datetime | None = None
    estimated_minutes: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: int | None = None
    status: str | None = None
    category_id: int | None = None
    due_date: datetime | None = None
    estimated_minutes: int | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    priority: int
    status: str
    category_id: int | None
    category: CategoryResponse | None = None
    due_date: datetime | None
    estimated_minutes: int | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


# --- Gamification ---

class StatsResponse(BaseModel):
    total_points: int
    current_streak: int
    longest_streak: int
    last_completion_date: date | None
    tasks_completed: int

    model_config = {"from_attributes": True}


class BadgeResponse(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    condition_type: str
    condition_value: int
    earned: bool = False
    earned_at: datetime | None = None

    model_config = {"from_attributes": True}


class TaskCompleteResponse(BaseModel):
    task: TaskResponse
    points_earned: int
    new_badges: list[BadgeResponse] = []
    stats: StatsResponse


# --- ML Predictions ---

class PredictionResponse(BaseModel):
    task_id: int
    completion_probability: float
    method: str  # "model" or "heuristic"
    confidence: str  # "high", "medium", "low"


class MLStatusResponse(BaseModel):
    trained: bool
    accuracy: float | None = None
    sample_count: int | None = None
    trained_at: str | None = None
