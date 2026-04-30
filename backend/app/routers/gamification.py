from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Badge, EarnedBadge
from app.schemas import StatsResponse, BadgeResponse
from app.services.gamification import get_stats

router = APIRouter(tags=["gamification"])


@router.get("/stats", response_model=StatsResponse)
def get_user_stats(db: Session = Depends(get_db)):
    return get_stats(db)


@router.get("/badges", response_model=list[BadgeResponse])
def list_badges(db: Session = Depends(get_db)):
    badges = db.query(Badge).all()
    earned_map = {}
    for eb in db.query(EarnedBadge).all():
        earned_map[eb.badge_id] = eb.earned_at

    result = []
    for badge in badges:
        is_earned = badge.id in earned_map
        result.append(BadgeResponse(
            id=badge.id,
            name=badge.name,
            description=badge.description,
            icon=badge.icon,
            condition_type=badge.condition_type,
            condition_value=badge.condition_value,
            earned=is_earned,
            earned_at=earned_map.get(badge.id),
        ))

    return result
