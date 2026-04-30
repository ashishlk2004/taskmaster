import json
import os
from datetime import datetime
import joblib
import numpy as np
from sqlalchemy.orm import Session
from app.models import Task, UserStats

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ml_models")
MODEL_PATH = os.path.join(MODEL_DIR, "completion_model.joblib")
META_PATH = os.path.join(MODEL_DIR, "model_meta.json")

MIN_SAMPLES = 20


def _extract_features(task: Task, stats: UserStats, total_tasks: int) -> list[float]:
    """Extract feature vector from a task and user stats."""
    completion_rate = stats.tasks_completed / max(total_tasks, 1)

    days_until_due = 0.0
    has_due_date = 0.0
    if task.due_date:
        has_due_date = 1.0
        reference = task.completed_at or datetime.utcnow()
        days_until_due = (task.due_date - task.created_at).total_seconds() / 86400

    desc_length = len(task.description) if task.description else 0
    day_of_week = task.created_at.weekday()
    hour_of_day = task.created_at.hour

    return [
        float(task.priority),
        has_due_date,
        float(task.estimated_minutes or 0),
        float(task.category_id or 0),
        float(day_of_week),
        float(hour_of_day),
        float(desc_length),
        days_until_due,
        float(stats.current_streak),
        completion_rate,
    ]


def train_model(db: Session) -> dict:
    """Train the completion prediction model on historical task data."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score

    # Get all terminal tasks: completed or overdue-and-still-pending
    all_tasks = db.query(Task).filter(
        (Task.status == "completed") |
        ((Task.status.in_(["pending", "in_progress"])) & (Task.due_date < datetime.utcnow()))
    ).all()

    if len(all_tasks) < MIN_SAMPLES:
        return {
            "trained": False,
            "error": f"Need at least {MIN_SAMPLES} completed/overdue tasks, have {len(all_tasks)}",
            "sample_count": len(all_tasks),
        }

    stats = db.query(UserStats).first()
    total_tasks = db.query(Task).count()

    X = []
    y = []
    for task in all_tasks:
        features = _extract_features(task, stats, total_tasks)
        X.append(features)
        y.append(1 if task.status == "completed" else 0)

    X = np.array(X)
    y = np.array(y)

    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
    scores = cross_val_score(model, X, y, cv=min(5, len(X)), scoring="accuracy")
    accuracy = float(scores.mean())

    # Train on full dataset
    model.fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    meta = {
        "trained": True,
        "accuracy": round(accuracy, 4),
        "sample_count": len(all_tasks),
        "trained_at": datetime.utcnow().isoformat(),
        "feature_names": [
            "priority", "has_due_date", "estimated_minutes", "category_id",
            "day_of_week", "hour_of_day", "description_length",
            "days_until_due", "current_streak", "completion_rate",
        ],
    }
    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)

    return meta


def predict_completion(db: Session, task: Task) -> dict:
    """Predict completion probability for a task."""
    stats = db.query(UserStats).first()
    total_tasks = db.query(Task).count()

    # Try model-based prediction
    if os.path.exists(MODEL_PATH) and os.path.exists(META_PATH):
        model = joblib.load(MODEL_PATH)
        features = np.array([_extract_features(task, stats, total_tasks)])
        probability = float(model.predict_proba(features)[0][1])

        with open(META_PATH) as f:
            meta = json.load(f)

        confidence = "high" if meta["accuracy"] > 0.8 else "medium" if meta["accuracy"] > 0.6 else "low"

        return {
            "task_id": task.id,
            "completion_probability": round(probability, 4),
            "method": "model",
            "confidence": confidence,
        }

    # Fallback heuristic
    return _heuristic_prediction(task, stats)


def _heuristic_prediction(task: Task, stats: UserStats) -> dict:
    """Simple heuristic when no trained model is available."""
    score = 0.5
    score += task.priority * 0.05
    if task.due_date:
        score += 0.15
    if stats.current_streak > 0:
        score += 0.1

    score = max(0.1, min(0.95, score))

    return {
        "task_id": task.id,
        "completion_probability": round(score, 4),
        "method": "heuristic",
        "confidence": "low",
    }


def get_model_status() -> dict:
    """Get current model status."""
    if os.path.exists(META_PATH):
        with open(META_PATH) as f:
            return json.load(f)
    return {"trained": False}
