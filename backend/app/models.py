from datetime import datetime, date
from sqlalchemy import Integer, String, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    color: Mapped[str] = mapped_column(String(7), default="#6366f1")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="category")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=2)  # 1=Low, 2=Medium, 3=High, 4=Urgent
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, in_progress, completed
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    estimated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    category: Mapped["Category | None"] = relationship("Category", back_populates="tasks")


class UserStats(Base):
    __tablename__ = "user_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0)


class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    icon: Mapped[str] = mapped_column(String(50), nullable=False)
    condition_type: Mapped[str] = mapped_column(String(50), nullable=False)  # tasks_completed, streak, points
    condition_value: Mapped[int] = mapped_column(Integer, nullable=False)

    earned: Mapped[list["EarnedBadge"]] = relationship("EarnedBadge", back_populates="badge")


class EarnedBadge(Base):
    __tablename__ = "earned_badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    badge_id: Mapped[int] = mapped_column(Integer, ForeignKey("badges.id"), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    badge: Mapped["Badge"] = relationship("Badge", back_populates="earned")
