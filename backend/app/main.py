from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine, SessionLocal
from app.models import UserStats, Badge, Category
from app.routers import tasks, categories, gamification, predictions


def seed_initial_data():
    """Seed default categories, badges, and user_stats on first run."""
    db = SessionLocal()
    try:
        # Create user_stats row if not exists
        if not db.query(UserStats).first():
            db.add(UserStats(id=1))

        # Seed default categories if not exists
        if db.query(Category).count() == 0:
            default_categories = [
                Category(name="Work", color="#3b82f6"),
                Category(name="Personal", color="#10b981"),
                Category(name="Health", color="#ef4444"),
                Category(name="Learning", color="#8b5cf6"),
                Category(name="Finance", color="#f59e0b"),
            ]
            db.add_all(default_categories)

        # Seed badges if not exists
        if db.query(Badge).count() == 0:
            badges = [
                Badge(name="First Step", description="Complete your first task", icon="🎯", condition_type="tasks_completed", condition_value=1),
                Badge(name="Getting Rolling", description="Complete 10 tasks", icon="🔥", condition_type="tasks_completed", condition_value=10),
                Badge(name="Quarter Century", description="Complete 25 tasks", icon="⭐", condition_type="tasks_completed", condition_value=25),
                Badge(name="Centurion", description="Complete 100 tasks", icon="💯", condition_type="tasks_completed", condition_value=100),
                Badge(name="On Fire", description="Maintain a 3-day streak", icon="🔥", condition_type="streak", condition_value=3),
                Badge(name="Streak Master", description="Maintain a 7-day streak", icon="⚡", condition_type="streak", condition_value=7),
                Badge(name="Unstoppable", description="Maintain a 30-day streak", icon="🏆", condition_type="streak", condition_value=30),
                Badge(name="Point Collector", description="Earn 100 points", icon="💰", condition_type="points", condition_value=100),
                Badge(name="High Achiever", description="Earn 500 points", icon="💎", condition_type="points", condition_value=500),
                Badge(name="Legend", description="Earn 1000 points", icon="👑", condition_type="points", condition_value=1000),
            ]
            db.add_all(badges)

        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_initial_data()
    yield


app = FastAPI(title="TaskMaster", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(gamification.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "TaskMaster API", "docs": "/docs"}
