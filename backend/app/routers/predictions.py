from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Task
from app.schemas import PredictionResponse, MLStatusResponse
from app.services.ml_predictor import predict_completion, train_model, get_model_status

router = APIRouter(tags=["predictions"])


@router.get("/tasks/{task_id}/predict", response_model=PredictionResponse)
def predict_task_completion(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    if task.status == "completed":
        raise HTTPException(400, "Task is already completed")
    return predict_completion(db, task)


@router.post("/ml/train")
def train_ml_model(db: Session = Depends(get_db)):
    result = train_model(db)
    return result


@router.get("/ml/status", response_model=MLStatusResponse)
def ml_status():
    return get_model_status()
