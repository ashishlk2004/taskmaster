from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskCompleteResponse
from app.services.gamification import award_points, update_streak, check_badges, get_stats

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    status: str | None = Query(None),
    category_id: int | None = Query(None),
    priority: int | None = Query(None),
    sort_by: str = Query("created_at"),
    db: Session = Depends(get_db),
):
    query = db.query(Task).options(joinedload(Task.category))
    if status:
        query = query.filter(Task.status == status)
    if category_id:
        query = query.filter(Task.category_id == category_id)
    if priority:
        query = query.filter(Task.priority == priority)

    sort_col = getattr(Task, sort_by, Task.created_at)
    if sort_by == "priority":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.desc())

    return query.all()


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).options(joinedload(Task.category)).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    db.delete(task)
    db.commit()


@router.post("/{task_id}/complete", response_model=TaskCompleteResponse)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).options(joinedload(Task.category)).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    if task.status == "completed":
        raise HTTPException(400, "Task already completed")

    task.status = "completed"
    task.completed_at = datetime.utcnow()

    points_earned = award_points(db, task)
    update_streak(db)
    new_badges = check_badges(db)
    stats = get_stats(db)

    db.commit()
    db.refresh(task)

    return TaskCompleteResponse(
        task=task,
        points_earned=points_earned,
        new_badges=new_badges,
        stats=stats,
    )
