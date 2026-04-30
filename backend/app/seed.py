"""Seed script to generate demo data for testing and ML training."""
import random
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Category, Task

CATEGORIES = [
    ("Work", "#3b82f6"),
    ("Personal", "#10b981"),
    ("Health", "#ef4444"),
    ("Learning", "#8b5cf6"),
    ("Finance", "#f59e0b"),
]

TASK_TEMPLATES = {
    "Work": [
        "Review pull requests", "Write project proposal", "Update documentation",
        "Fix login bug", "Deploy staging build", "Team standup prep",
        "Refactor auth module", "Write unit tests", "Code review feedback",
        "Sprint planning notes", "Update API endpoints", "Database migration",
    ],
    "Personal": [
        "Grocery shopping", "Clean apartment", "Call mom",
        "Organize closet", "Plan weekend trip", "Return package",
        "Fix leaky faucet", "Renew subscription", "Backup photos",
        "Update resume", "Read 30 pages", "Meal prep Sunday",
    ],
    "Health": [
        "Morning run", "Gym session", "Yoga class",
        "Schedule dentist", "Meal prep healthy lunches", "Drink 8 glasses water",
        "30 min meditation", "Evening walk", "Track calories",
        "Annual checkup", "Buy vitamins", "Stretch routine",
    ],
    "Learning": [
        "Complete Python tutorial", "Watch ML lecture", "Practice algorithms",
        "Read design patterns chapter", "Build side project", "Take online quiz",
        "Review flashcards", "Write blog post", "Learn Docker basics",
        "Study system design", "Practice SQL queries", "Read tech article",
    ],
    "Finance": [
        "Review monthly budget", "Pay credit card", "File expense report",
        "Check investment portfolio", "Cancel unused subscription", "Set savings goal",
        "Compare insurance rates", "Update spreadsheet", "Tax document prep",
        "Review bank statements", "Negotiate bill", "Research ETFs",
    ],
}


def seed_demo_data():
    """Generate 60 demo tasks with realistic patterns."""
    db = SessionLocal()
    try:
        # Skip if data already exists
        if db.query(Task).count() > 0:
            print("Demo data already exists, skipping seed.")
            return

        # Create categories (or look up existing ones)
        cat_map = {}
        for name, color in CATEGORIES:
            existing = db.query(Category).filter(Category.name == name).first()
            if existing:
                cat_map[name] = existing.id
            else:
                cat = Category(name=name, color=color)
                db.add(cat)
                db.flush()
                cat_map[name] = cat.id

        now = datetime.utcnow()
        tasks = []

        for cat_name, templates in TASK_TEMPLATES.items():
            for i, title in enumerate(templates):
                # Spread creation dates over the past 30 days
                days_ago = random.randint(0, 30)
                hours_ago = random.randint(0, 23)
                created = now - timedelta(days=days_ago, hours=hours_ago)

                priority = random.choices([1, 2, 3, 4], weights=[20, 40, 25, 15])[0]
                estimated = random.choice([15, 30, 45, 60, 90, 120, None])

                # 70% chance of having a due date
                due_date = None
                if random.random() < 0.7:
                    due_date = created + timedelta(days=random.randint(1, 14))

                # Determine status with realistic completion patterns
                # Higher priority tasks are more likely completed
                completion_chance = {1: 0.4, 2: 0.55, 3: 0.7, 4: 0.8}
                is_completed = random.random() < completion_chance[priority]

                status = "completed" if is_completed else random.choice(["pending", "in_progress"])
                completed_at = None
                if is_completed:
                    # Complete within 1-7 days of creation
                    completed_at = created + timedelta(
                        days=random.randint(0, 5),
                        hours=random.randint(1, 12),
                    )

                description = f"Task: {title} in {cat_name} category."
                if estimated:
                    description += f" Estimated time: {estimated} minutes."

                task = Task(
                    title=title,
                    description=description,
                    priority=priority,
                    status=status,
                    category_id=cat_map[cat_name],
                    due_date=due_date,
                    estimated_minutes=estimated,
                    created_at=created,
                    completed_at=completed_at,
                )
                tasks.append(task)

        db.add_all(tasks)
        db.commit()
        print(f"Seeded {len(tasks)} demo tasks across {len(CATEGORIES)} categories.")

    finally:
        db.close()


if __name__ == "__main__":
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)
    seed_demo_data()
