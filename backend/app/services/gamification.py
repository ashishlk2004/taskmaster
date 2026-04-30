from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models import UserStats, Badge, EarnedBadge, Task
from app.schemas import BadgeResponse, StatsResponse


def get_stats(db: Session) -> StatsResponse:
    stats = db.query(UserStats).first()
    return StatsResponse.model_validate(stats)


def award_points(db: Session, task: Task) -> int:
    """Calculate and award points for completing a task."""
    stats = db.query(UserStats).first()

    # Base points
    base = 10

    # Priority multiplier
    multipliers = {1: 1.0, 2: 1.5, 3: 2.0, 4: 3.0}
    multiplier = multipliers.get(task.priority, 1.0)

    points = int(base * multiplier)

    # On-time bonus
    if task.due_date and task.completed_at and task.completed_at <= task.due_date:
        points += 5

    # Streak bonus
    if stats.current_streak > 0:
        points += min(stats.current_streak * 2, 20)  # Cap streak bonus at 20

    stats.total_points += points
    stats.tasks_completed += 1

    return points


def update_streak(db: Session):
    """Update the user's completion streak."""
    stats = db.query(UserStats).first()
    today = date.today()

    if stats.last_completion_date is None:
        stats.current_streak = 1
    elif stats.last_completion_date == today:
        # Already completed a task today, streak stays the same
        pass
    elif (today - stats.last_completion_date).days == 1:
        # Consecutive day
        stats.current_streak += 1
    else:
        # Streak broken
        stats.current_streak = 1

    stats.last_completion_date = today
    stats.longest_streak = max(stats.longest_streak, stats.current_streak)


def check_badges(db: Session) -> list[BadgeResponse]:
    """Check and award any newly earned badges. Returns list of newly earned badges."""
    stats = db.query(UserStats).first()
    all_badges = db.query(Badge).all()
    earned_ids = {eb.badge_id for eb in db.query(EarnedBadge).all()}

    new_badges = []

    condition_map = {
        "tasks_completed": stats.tasks_completed,
        "streak": stats.current_streak,
        "points": stats.total_points,
    }

    for badge in all_badges:
        if badge.id in earned_ids:
            continue

        current_value = condition_map.get(badge.condition_type, 0)
        if current_value >= badge.condition_value:
            earned = EarnedBadge(badge_id=badge.id)
            db.add(earned)
            new_badges.append(BadgeResponse(
                id=badge.id,
                name=badge.name,
                description=badge.description,
                icon=badge.icon,
                condition_type=badge.condition_type,
                condition_value=badge.condition_value,
                earned=True,
                earned_at=datetime.utcnow(),
            ))

    return new_badges
