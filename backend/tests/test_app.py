import pytest
from datetime import datetime, date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app, seed_initial_data
from app.models import Task, Category, UserStats, Badge, EarnedBadge
from app.services.gamification import award_points, update_streak, check_badges, get_stats


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(name="engine")
def fixture_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="db_session")
def fixture_db_session(engine):
    """Create a fresh database session for each test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(name="seeded_db")
def fixture_seeded_db(engine, db_session):
    """Session with seed data (UserStats + Badges) pre-loaded."""
    # Seed UserStats
    db_session.add(UserStats(id=1))
    # Seed Badges (same as main.py seed_initial_data)
    badges = [
        Badge(name="First Step", description="Complete your first task", icon="t", condition_type="tasks_completed", condition_value=1),
        Badge(name="Getting Rolling", description="Complete 10 tasks", icon="f", condition_type="tasks_completed", condition_value=10),
        Badge(name="Quarter Century", description="Complete 25 tasks", icon="s", condition_type="tasks_completed", condition_value=25),
        Badge(name="Centurion", description="Complete 100 tasks", icon="c", condition_type="tasks_completed", condition_value=100),
        Badge(name="On Fire", description="Maintain a 3-day streak", icon="f", condition_type="streak", condition_value=3),
        Badge(name="Streak Master", description="Maintain a 7-day streak", icon="z", condition_type="streak", condition_value=7),
        Badge(name="Unstoppable", description="Maintain a 30-day streak", icon="t", condition_type="streak", condition_value=30),
        Badge(name="Point Collector", description="Earn 100 points", icon="p", condition_type="points", condition_value=100),
        Badge(name="High Achiever", description="Earn 500 points", icon="d", condition_type="points", condition_value=500),
        Badge(name="Legend", description="Earn 1000 points", icon="c", condition_type="points", condition_value=1000),
    ]
    db_session.add_all(badges)
    db_session.commit()
    yield db_session


@pytest.fixture(name="client")
def fixture_client(engine):
    """FastAPI TestClient that uses the in-memory database."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    # Seed data using the test database
    session = TestingSessionLocal()
    try:
        if not session.query(UserStats).first():
            session.add(UserStats(id=1))
        if session.query(Badge).count() == 0:
            badges = [
                Badge(name="First Step", description="Complete your first task", icon="t", condition_type="tasks_completed", condition_value=1),
                Badge(name="Getting Rolling", description="Complete 10 tasks", icon="f", condition_type="tasks_completed", condition_value=10),
                Badge(name="Quarter Century", description="Complete 25 tasks", icon="s", condition_type="tasks_completed", condition_value=25),
                Badge(name="Centurion", description="Complete 100 tasks", icon="c", condition_type="tasks_completed", condition_value=100),
                Badge(name="On Fire", description="Maintain a 3-day streak", icon="f", condition_type="streak", condition_value=3),
                Badge(name="Streak Master", description="Maintain a 7-day streak", icon="z", condition_type="streak", condition_value=7),
                Badge(name="Unstoppable", description="Maintain a 30-day streak", icon="t", condition_type="streak", condition_value=30),
                Badge(name="Point Collector", description="Earn 100 points", icon="p", condition_type="points", condition_value=100),
                Badge(name="High Achiever", description="Earn 500 points", icon="d", condition_type="points", condition_value=500),
                Badge(name="Legend", description="Earn 1000 points", icon="c", condition_type="points", condition_value=1000),
            ]
            session.add_all(badges)
        session.commit()
    finally:
        session.close()

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

    app.dependency_overrides.clear()


# ===========================================================================
# UNIT TESTS -- Gamification Service
# ===========================================================================

class TestAwardPoints:
    """Unit tests for the award_points() function."""

    def test_base_points_medium_priority(self, seeded_db):
        """Medium priority (2) task earns 10 * 1.5 = 15 base points."""
        task = Task(
            id=1, title="Test", priority=2, status="completed",
            completed_at=datetime.utcnow(),
        )
        seeded_db.add(task)
        seeded_db.flush()

        points = award_points(seeded_db, task)

        assert points == 15  # 10 * 1.5

    def test_base_points_low_priority(self, seeded_db):
        """Low priority (1) task earns 10 * 1.0 = 10 base points."""
        task = Task(
            id=1, title="Test", priority=1, status="completed",
            completed_at=datetime.utcnow(),
        )
        seeded_db.add(task)
        seeded_db.flush()

        points = award_points(seeded_db, task)

        assert points == 10  # 10 * 1.0

    def test_base_points_high_priority(self, seeded_db):
        """High priority (3) task earns 10 * 2.0 = 20 base points."""
        task = Task(
            id=1, title="Test", priority=3, status="completed",
            completed_at=datetime.utcnow(),
        )
        seeded_db.add(task)
        seeded_db.flush()

        points = award_points(seeded_db, task)

        assert points == 20  # 10 * 2.0

    def test_base_points_urgent_priority(self, seeded_db):
        """Urgent priority (4) task earns 10 * 3.0 = 30 base points."""
        task = Task(
            id=1, title="Test", priority=4, status="completed",
            completed_at=datetime.utcnow(),
        )
        seeded_db.add(task)
        seeded_db.flush()

        points = award_points(seeded_db, task)

        assert points == 30  # 10 * 3.0

    def test_on_time_bonus(self, seeded_db):
        """Completing a task before its due date earns +5 bonus points."""
        due = datetime.utcnow() + timedelta(days=1)
        completed = datetime.utcnow()
        task = Task(
            id=1, title="Test", priority=1, status="completed",
            due_date=due, completed_at=completed,
        )
        seeded_db.add(task)
        seeded_db.flush()

        points = award_points(seeded_db, task)

        assert points == 15  # 10 base + 5 on-time bonus

    def test_no_on_time_bonus_when_late(self, seeded_db):
        """Completing a task after its due date earns no on-time bonus."""
        due = datetime.utcnow() - timedelta(days=1)
        completed = datetime.utcnow()
        task = Task(
            id=1, title="Test", priority=1, status="completed",
            due_date=due, completed_at=completed,
        )
        seeded_db.add(task)
        seeded_db.flush()

        points = award_points(seeded_db, task)

        assert points == 10  # 10 base, no bonus

    def test_streak_bonus(self, seeded_db):
        """Active streak adds streak*2 bonus points (capped at 20)."""
        stats = seeded_db.query(UserStats).first()
        stats.current_streak = 5
        seeded_db.flush()

        task = Task(
            id=1, title="Test", priority=1, status="completed",
            completed_at=datetime.utcnow(),
        )
        seeded_db.add(task)
        seeded_db.flush()

        points = award_points(seeded_db, task)

        assert points == 20  # 10 base + 5*2=10 streak bonus

    def test_streak_bonus_capped_at_20(self, seeded_db):
        """Streak bonus is capped at 20 points even for very long streaks."""
        stats = seeded_db.query(UserStats).first()
        stats.current_streak = 50
        seeded_db.flush()

        task = Task(
            id=1, title="Test", priority=1, status="completed",
            completed_at=datetime.utcnow(),
        )
        seeded_db.add(task)
        seeded_db.flush()

        points = award_points(seeded_db, task)

        assert points == 30  # 10 base + 20 capped streak bonus

    def test_points_accumulated_in_stats(self, seeded_db):
        """Award points updates total_points and tasks_completed in UserStats."""
        task = Task(
            id=1, title="Test", priority=2, status="completed",
            completed_at=datetime.utcnow(),
        )
        seeded_db.add(task)
        seeded_db.flush()

        award_points(seeded_db, task)

        stats = seeded_db.query(UserStats).first()
        assert stats.total_points == 15
        assert stats.tasks_completed == 1

    def test_combined_bonuses(self, seeded_db):
        """High priority + on-time + streak all stack together."""
        stats = seeded_db.query(UserStats).first()
        stats.current_streak = 3
        seeded_db.flush()

        due = datetime.utcnow() + timedelta(days=1)
        task = Task(
            id=1, title="Test", priority=4, status="completed",
            due_date=due, completed_at=datetime.utcnow(),
        )
        seeded_db.add(task)
        seeded_db.flush()

        points = award_points(seeded_db, task)

        # 10*3.0 = 30 base + 5 on-time + min(3*2, 20)=6 streak = 41
        assert points == 41


class TestUpdateStreak:
    """Unit tests for the update_streak() function."""

    def test_first_completion_sets_streak_to_1(self, seeded_db):
        """First ever task completion starts streak at 1."""
        update_streak(seeded_db)

        stats = seeded_db.query(UserStats).first()
        assert stats.current_streak == 1
        assert stats.last_completion_date == date.today()
        assert stats.longest_streak == 1

    def test_same_day_completion_keeps_streak(self, seeded_db):
        """Completing another task on the same day does not change streak."""
        stats = seeded_db.query(UserStats).first()
        stats.current_streak = 3
        stats.last_completion_date = date.today()
        stats.longest_streak = 3
        seeded_db.flush()

        update_streak(seeded_db)

        stats = seeded_db.query(UserStats).first()
        assert stats.current_streak == 3

    def test_consecutive_day_increments_streak(self, seeded_db):
        """Completing on the next day increments the streak."""
        stats = seeded_db.query(UserStats).first()
        stats.current_streak = 2
        stats.last_completion_date = date.today() - timedelta(days=1)
        stats.longest_streak = 2
        seeded_db.flush()

        update_streak(seeded_db)

        stats = seeded_db.query(UserStats).first()
        assert stats.current_streak == 3
        assert stats.longest_streak == 3

    def test_gap_resets_streak(self, seeded_db):
        """Missing a day resets the streak to 1."""
        stats = seeded_db.query(UserStats).first()
        stats.current_streak = 5
        stats.last_completion_date = date.today() - timedelta(days=3)
        stats.longest_streak = 5
        seeded_db.flush()

        update_streak(seeded_db)

        stats = seeded_db.query(UserStats).first()
        assert stats.current_streak == 1
        assert stats.longest_streak == 5  # longest preserved

    def test_longest_streak_preserved(self, seeded_db):
        """Longest streak is never decreased, only updated when exceeded."""
        stats = seeded_db.query(UserStats).first()
        stats.current_streak = 10
        stats.last_completion_date = date.today() - timedelta(days=5)
        stats.longest_streak = 10
        seeded_db.flush()

        update_streak(seeded_db)

        stats = seeded_db.query(UserStats).first()
        assert stats.current_streak == 1
        assert stats.longest_streak == 10


class TestCheckBadges:
    """Unit tests for the check_badges() function."""

    def test_earn_first_step_badge(self, seeded_db):
        """Completing 1 task earns the 'First Step' badge."""
        stats = seeded_db.query(UserStats).first()
        stats.tasks_completed = 1
        stats.total_points = 10
        seeded_db.flush()

        new_badges = check_badges(seeded_db)

        badge_names = [b.name for b in new_badges]
        assert "First Step" in badge_names

    def test_no_duplicate_badges(self, seeded_db):
        """Already earned badges are not re-awarded."""
        stats = seeded_db.query(UserStats).first()
        stats.tasks_completed = 1
        stats.total_points = 10
        seeded_db.flush()

        # Earn badges first time
        check_badges(seeded_db)
        seeded_db.flush()

        # Check again -- should return empty
        new_badges = check_badges(seeded_db)

        assert len(new_badges) == 0

    def test_multiple_badges_at_once(self, seeded_db):
        """Meeting multiple conditions at once awards all applicable badges."""
        stats = seeded_db.query(UserStats).first()
        stats.tasks_completed = 10
        stats.total_points = 150
        stats.current_streak = 3
        seeded_db.flush()

        new_badges = check_badges(seeded_db)

        badge_names = {b.name for b in new_badges}
        assert "First Step" in badge_names
        assert "Getting Rolling" in badge_names
        assert "Point Collector" in badge_names
        assert "On Fire" in badge_names

    def test_streak_badge(self, seeded_db):
        """Streak of 7 earns 'Streak Master' badge."""
        stats = seeded_db.query(UserStats).first()
        stats.current_streak = 7
        seeded_db.flush()

        new_badges = check_badges(seeded_db)

        badge_names = {b.name for b in new_badges}
        assert "Streak Master" in badge_names

    def test_points_badge(self, seeded_db):
        """Earning 500 points awards 'High Achiever' badge."""
        stats = seeded_db.query(UserStats).first()
        stats.total_points = 500
        seeded_db.flush()

        new_badges = check_badges(seeded_db)

        badge_names = {b.name for b in new_badges}
        assert "Point Collector" in badge_names
        assert "High Achiever" in badge_names


class TestGetStats:
    """Unit tests for the get_stats() function."""

    def test_initial_stats(self, seeded_db):
        """Fresh stats have all zeros."""
        stats = get_stats(seeded_db)

        assert stats.total_points == 0
        assert stats.current_streak == 0
        assert stats.longest_streak == 0
        assert stats.tasks_completed == 0
        assert stats.last_completion_date is None


# ===========================================================================
# INTEGRATION TESTS -- API Endpoints
# ===========================================================================

class TestCategoryEndpoints:
    """Integration tests for the /api/v1/categories endpoints."""

    def test_create_category(self, client):
        """POST /api/v1/categories creates a new category."""
        resp = client.post("/api/v1/categories", json={"name": "Work", "color": "#ff0000"})

        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Work"
        assert data["color"] == "#ff0000"
        assert "id" in data

    def test_create_duplicate_category_fails(self, client):
        """Duplicate category name returns 400."""
        client.post("/api/v1/categories", json={"name": "Work"})
        resp = client.post("/api/v1/categories", json={"name": "Work"})

        assert resp.status_code == 400

    def test_list_categories(self, client):
        """GET /api/v1/categories returns all categories."""
        client.post("/api/v1/categories", json={"name": "Alpha"})
        client.post("/api/v1/categories", json={"name": "Beta"})

        resp = client.get("/api/v1/categories")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        # Should be sorted by name
        assert data[0]["name"] == "Alpha"
        assert data[1]["name"] == "Beta"

    def test_update_category(self, client):
        """PUT /api/v1/categories/{id} updates name and color."""
        create_resp = client.post("/api/v1/categories", json={"name": "Old", "color": "#000000"})
        cat_id = create_resp.json()["id"]

        resp = client.put(f"/api/v1/categories/{cat_id}", json={"name": "New", "color": "#ffffff"})

        assert resp.status_code == 200
        assert resp.json()["name"] == "New"
        assert resp.json()["color"] == "#ffffff"

    def test_update_nonexistent_category(self, client):
        """PUT on a non-existent category returns 404."""
        resp = client.put("/api/v1/categories/999", json={"name": "X"})

        assert resp.status_code == 404

    def test_delete_category(self, client):
        """DELETE /api/v1/categories/{id} removes the category."""
        create_resp = client.post("/api/v1/categories", json={"name": "Temp"})
        cat_id = create_resp.json()["id"]

        resp = client.delete(f"/api/v1/categories/{cat_id}")

        assert resp.status_code == 204

        # Verify it is gone
        list_resp = client.get("/api/v1/categories")
        names = [c["name"] for c in list_resp.json()]
        assert "Temp" not in names

    def test_delete_nonexistent_category(self, client):
        """DELETE on a non-existent category returns 404."""
        resp = client.delete("/api/v1/categories/999")

        assert resp.status_code == 404


class TestTaskEndpoints:
    """Integration tests for the /api/v1/tasks endpoints."""

    def test_create_task(self, client):
        """POST /api/v1/tasks creates a new task with defaults."""
        resp = client.post("/api/v1/tasks", json={"title": "Buy groceries"})

        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Buy groceries"
        assert data["status"] == "pending"
        assert data["priority"] == 2

    def test_create_task_with_all_fields(self, client):
        """POST /api/v1/tasks with all optional fields set."""
        cat_resp = client.post("/api/v1/categories", json={"name": "Personal"})
        cat_id = cat_resp.json()["id"]

        payload = {
            "title": "Doctor appointment",
            "description": "Annual checkup",
            "priority": 3,
            "category_id": cat_id,
            "due_date": "2026-12-31T23:59:59",
            "estimated_minutes": 60,
        }
        resp = client.post("/api/v1/tasks", json=payload)

        assert resp.status_code == 201
        data = resp.json()
        assert data["description"] == "Annual checkup"
        assert data["priority"] == 3
        assert data["category_id"] == cat_id
        assert data["estimated_minutes"] == 60

    def test_list_tasks(self, client):
        """GET /api/v1/tasks returns all tasks."""
        client.post("/api/v1/tasks", json={"title": "Task A"})
        client.post("/api/v1/tasks", json={"title": "Task B"})

        resp = client.get("/api/v1/tasks")

        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_tasks_filter_by_status(self, client):
        """GET /api/v1/tasks?status=pending filters tasks."""
        client.post("/api/v1/tasks", json={"title": "Pending task"})

        resp = client.get("/api/v1/tasks", params={"status": "pending"})

        assert resp.status_code == 200
        assert all(t["status"] == "pending" for t in resp.json())

    def test_list_tasks_filter_by_priority(self, client):
        """GET /api/v1/tasks?priority=3 filters by priority."""
        client.post("/api/v1/tasks", json={"title": "Low", "priority": 1})
        client.post("/api/v1/tasks", json={"title": "High", "priority": 3})

        resp = client.get("/api/v1/tasks", params={"priority": 3})

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "High"

    def test_list_tasks_filter_by_category(self, client):
        """GET /api/v1/tasks?category_id=X filters by category."""
        cat_resp = client.post("/api/v1/categories", json={"name": "Work"})
        cat_id = cat_resp.json()["id"]

        client.post("/api/v1/tasks", json={"title": "Work task", "category_id": cat_id})
        client.post("/api/v1/tasks", json={"title": "No category task"})

        resp = client.get("/api/v1/tasks", params={"category_id": cat_id})

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "Work task"

    def test_get_single_task(self, client):
        """GET /api/v1/tasks/{id} returns the specific task."""
        create_resp = client.post("/api/v1/tasks", json={"title": "Specific task"})
        task_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/tasks/{task_id}")

        assert resp.status_code == 200
        assert resp.json()["title"] == "Specific task"

    def test_get_nonexistent_task(self, client):
        """GET /api/v1/tasks/999 returns 404."""
        resp = client.get("/api/v1/tasks/999")

        assert resp.status_code == 404

    def test_update_task(self, client):
        """PUT /api/v1/tasks/{id} updates specified fields."""
        create_resp = client.post("/api/v1/tasks", json={"title": "Original"})
        task_id = create_resp.json()["id"]

        resp = client.put(f"/api/v1/tasks/{task_id}", json={"title": "Updated", "priority": 4})

        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Updated"
        assert data["priority"] == 4

    def test_update_task_status(self, client):
        """PUT /api/v1/tasks/{id} can change status to in_progress."""
        create_resp = client.post("/api/v1/tasks", json={"title": "Task"})
        task_id = create_resp.json()["id"]

        resp = client.put(f"/api/v1/tasks/{task_id}", json={"status": "in_progress"})

        assert resp.status_code == 200
        assert resp.json()["status"] == "in_progress"

    def test_update_nonexistent_task(self, client):
        """PUT on a non-existent task returns 404."""
        resp = client.put("/api/v1/tasks/999", json={"title": "X"})

        assert resp.status_code == 404

    def test_delete_task(self, client):
        """DELETE /api/v1/tasks/{id} removes the task."""
        create_resp = client.post("/api/v1/tasks", json={"title": "Delete me"})
        task_id = create_resp.json()["id"]

        resp = client.delete(f"/api/v1/tasks/{task_id}")

        assert resp.status_code == 204

        # Verify removal
        get_resp = client.get(f"/api/v1/tasks/{task_id}")
        assert get_resp.status_code == 404

    def test_delete_nonexistent_task(self, client):
        """DELETE on a non-existent task returns 404."""
        resp = client.delete("/api/v1/tasks/999")

        assert resp.status_code == 404


class TestTaskCompletionEndpoint:
    """Integration tests for the POST /api/v1/tasks/{id}/complete endpoint."""

    def test_complete_task(self, client):
        """Completing a task returns points, stats, and task with completed status."""
        create_resp = client.post("/api/v1/tasks", json={"title": "Finish report", "priority": 2})
        task_id = create_resp.json()["id"]

        resp = client.post(f"/api/v1/tasks/{task_id}/complete")

        assert resp.status_code == 200
        data = resp.json()
        assert data["task"]["status"] == "completed"
        assert data["task"]["completed_at"] is not None
        assert data["points_earned"] > 0
        assert "stats" in data
        assert data["stats"]["tasks_completed"] == 1

    def test_complete_already_completed_task(self, client):
        """Completing an already completed task returns 400."""
        create_resp = client.post("/api/v1/tasks", json={"title": "Done"})
        task_id = create_resp.json()["id"]

        client.post(f"/api/v1/tasks/{task_id}/complete")
        resp = client.post(f"/api/v1/tasks/{task_id}/complete")

        assert resp.status_code == 400

    def test_complete_nonexistent_task(self, client):
        """Completing a non-existent task returns 404."""
        resp = client.post("/api/v1/tasks/999/complete")

        assert resp.status_code == 404

    def test_complete_task_earns_badge(self, client):
        """First task completion earns the 'First Step' badge."""
        create_resp = client.post("/api/v1/tasks", json={"title": "First!"})
        task_id = create_resp.json()["id"]

        resp = client.post(f"/api/v1/tasks/{task_id}/complete")

        data = resp.json()
        badge_names = [b["name"] for b in data["new_badges"]]
        assert "First Step" in badge_names

    def test_complete_high_priority_gives_more_points(self, client):
        """Higher priority tasks yield more points."""
        # Create low and high priority tasks
        low_resp = client.post("/api/v1/tasks", json={"title": "Low", "priority": 1})
        high_resp = client.post("/api/v1/tasks", json={"title": "High", "priority": 4})

        low_complete = client.post(f"/api/v1/tasks/{low_resp.json()['id']}/complete")
        high_complete = client.post(f"/api/v1/tasks/{high_resp.json()['id']}/complete")

        assert high_complete.json()["points_earned"] > low_complete.json()["points_earned"]


class TestGamificationEndpoints:
    """Integration tests for /api/v1/stats and /api/v1/badges."""

    def test_get_initial_stats(self, client):
        """GET /api/v1/stats returns zero stats initially."""
        resp = client.get("/api/v1/stats")

        assert resp.status_code == 200
        data = resp.json()
        assert data["total_points"] == 0
        assert data["current_streak"] == 0
        assert data["tasks_completed"] == 0

    def test_get_badges(self, client):
        """GET /api/v1/badges returns all 10 seeded badges."""
        resp = client.get("/api/v1/badges")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 10
        assert all(b["earned"] is False for b in data)

    def test_badges_show_earned_after_completion(self, client):
        """After completing a task, badges endpoint shows earned status."""
        create_resp = client.post("/api/v1/tasks", json={"title": "Badge test"})
        task_id = create_resp.json()["id"]
        client.post(f"/api/v1/tasks/{task_id}/complete")

        resp = client.get("/api/v1/badges")

        data = resp.json()
        first_step = next(b for b in data if b["name"] == "First Step")
        assert first_step["earned"] is True
        assert first_step["earned_at"] is not None

    def test_stats_updated_after_completion(self, client):
        """Stats reflect changes after task completion."""
        create_resp = client.post("/api/v1/tasks", json={"title": "Stats test", "priority": 3})
        task_id = create_resp.json()["id"]
        client.post(f"/api/v1/tasks/{task_id}/complete")

        resp = client.get("/api/v1/stats")

        data = resp.json()
        assert data["tasks_completed"] == 1
        assert data["total_points"] > 0
        assert data["current_streak"] == 1


class TestPredictionEndpoints:
    """Integration tests for /api/v1/tasks/{id}/predict and /api/v1/ml/*."""

    def test_predict_task_heuristic(self, client):
        """Prediction uses heuristic fallback when no model is trained."""
        create_resp = client.post("/api/v1/tasks", json={"title": "Predict me", "priority": 3})
        task_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/tasks/{task_id}/predict")

        assert resp.status_code == 200
        data = resp.json()
        assert data["task_id"] == task_id
        assert data["method"] == "heuristic"
        assert data["confidence"] == "low"
        assert 0.0 <= data["completion_probability"] <= 1.0

    def test_predict_completed_task_fails(self, client):
        """Predicting a completed task returns 400."""
        create_resp = client.post("/api/v1/tasks", json={"title": "Done"})
        task_id = create_resp.json()["id"]
        client.post(f"/api/v1/tasks/{task_id}/complete")

        resp = client.get(f"/api/v1/tasks/{task_id}/predict")

        assert resp.status_code == 400

    def test_predict_nonexistent_task(self, client):
        """Predicting a non-existent task returns 404."""
        resp = client.get("/api/v1/tasks/999/predict")

        assert resp.status_code == 404

    def test_ml_status_untrained(self, client):
        """ML status reports untrained when no model exists."""
        resp = client.get("/api/v1/ml/status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["trained"] is False

    def test_train_with_insufficient_data(self, client):
        """Training with too few samples returns a failure message."""
        resp = client.post("/api/v1/ml/train")

        assert resp.status_code == 200
        data = resp.json()
        assert data["trained"] is False


class TestRootEndpoint:
    """Integration tests for the root endpoint."""

    def test_root(self, client):
        """GET / returns welcome message."""
        resp = client.get("/")

        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "TaskMaster API"


# ===========================================================================
# SYSTEM TESTS -- Full End-to-End Workflows
# ===========================================================================

class TestFullWorkflow:
    """System tests verifying complete user workflows across multiple modules."""

    def test_create_category_create_task_complete_verify(self, client):
        """Full workflow: create category -> create task -> complete -> verify stats/badges."""
        # Step 1: Create a category
        cat_resp = client.post("/api/v1/categories", json={"name": "Study", "color": "#00ff00"})
        assert cat_resp.status_code == 201
        cat_id = cat_resp.json()["id"]

        # Step 2: Create a task in that category
        task_resp = client.post("/api/v1/tasks", json={
            "title": "Read chapter 5",
            "description": "Read and take notes",
            "priority": 3,
            "category_id": cat_id,
            "estimated_minutes": 45,
        })
        assert task_resp.status_code == 201
        task_id = task_resp.json()["id"]
        assert task_resp.json()["category"]["name"] == "Study"

        # Step 3: Complete the task
        complete_resp = client.post(f"/api/v1/tasks/{task_id}/complete")
        assert complete_resp.status_code == 200
        complete_data = complete_resp.json()

        # Verify task is marked completed
        assert complete_data["task"]["status"] == "completed"
        assert complete_data["task"]["completed_at"] is not None

        # Verify points awarded (priority 3 = 10 * 2.0 = 20 base)
        assert complete_data["points_earned"] >= 20

        # Verify 'First Step' badge earned
        badge_names = [b["name"] for b in complete_data["new_badges"]]
        assert "First Step" in badge_names

        # Verify stats
        assert complete_data["stats"]["tasks_completed"] == 1
        assert complete_data["stats"]["current_streak"] == 1
        assert complete_data["stats"]["total_points"] >= 20

        # Step 4: Verify via independent stats endpoint
        stats_resp = client.get("/api/v1/stats")
        assert stats_resp.json()["tasks_completed"] == 1

        # Step 5: Verify via badges endpoint
        badges_resp = client.get("/api/v1/badges")
        first_step = next(b for b in badges_resp.json() if b["name"] == "First Step")
        assert first_step["earned"] is True

    def test_multiple_task_completion_workflow(self, client):
        """Workflow: complete multiple tasks and verify cumulative stats."""
        tasks_created = []
        for i in range(3):
            resp = client.post("/api/v1/tasks", json={
                "title": f"Task {i+1}",
                "priority": i + 1,  # priorities 1, 2, 3
            })
            tasks_created.append(resp.json()["id"])

        total_points = 0
        for task_id in tasks_created:
            resp = client.post(f"/api/v1/tasks/{task_id}/complete")
            total_points += resp.json()["points_earned"]

        # Verify cumulative stats
        stats_resp = client.get("/api/v1/stats")
        stats = stats_resp.json()
        assert stats["tasks_completed"] == 3
        assert stats["total_points"] == total_points
        assert stats["current_streak"] >= 1

    def test_task_lifecycle_workflow(self, client):
        """Workflow: create -> update status -> complete -> verify cannot re-complete."""
        # Create
        create_resp = client.post("/api/v1/tasks", json={"title": "Lifecycle task"})
        task_id = create_resp.json()["id"]
        assert create_resp.json()["status"] == "pending"

        # Update to in_progress
        update_resp = client.put(f"/api/v1/tasks/{task_id}", json={"status": "in_progress"})
        assert update_resp.json()["status"] == "in_progress"

        # Complete
        complete_resp = client.post(f"/api/v1/tasks/{task_id}/complete")
        assert complete_resp.status_code == 200
        assert complete_resp.json()["task"]["status"] == "completed"

        # Try to re-complete -- should fail
        re_complete_resp = client.post(f"/api/v1/tasks/{task_id}/complete")
        assert re_complete_resp.status_code == 400

    def test_category_task_relationship_workflow(self, client):
        """Workflow: categories and tasks maintain proper relationships."""
        # Create two categories
        cat1 = client.post("/api/v1/categories", json={"name": "Work"}).json()
        cat2 = client.post("/api/v1/categories", json={"name": "Personal"}).json()

        # Create tasks in each
        client.post("/api/v1/tasks", json={"title": "Work task 1", "category_id": cat1["id"]})
        client.post("/api/v1/tasks", json={"title": "Work task 2", "category_id": cat1["id"]})
        client.post("/api/v1/tasks", json={"title": "Personal task", "category_id": cat2["id"]})

        # Filter by category
        work_tasks = client.get("/api/v1/tasks", params={"category_id": cat1["id"]}).json()
        assert len(work_tasks) == 2

        personal_tasks = client.get("/api/v1/tasks", params={"category_id": cat2["id"]}).json()
        assert len(personal_tasks) == 1

    def test_prediction_workflow(self, client):
        """Workflow: create task -> get prediction -> complete -> prediction fails."""
        # Create a task
        task_resp = client.post("/api/v1/tasks", json={
            "title": "Predict and complete",
            "priority": 2,
            "due_date": "2026-12-31T23:59:59",
        })
        task_id = task_resp.json()["id"]

        # Get prediction (heuristic since no model trained)
        pred_resp = client.get(f"/api/v1/tasks/{task_id}/predict")
        assert pred_resp.status_code == 200
        assert pred_resp.json()["method"] == "heuristic"
        assert pred_resp.json()["completion_probability"] > 0

        # Complete the task
        client.post(f"/api/v1/tasks/{task_id}/complete")

        # Prediction should now fail (task completed)
        pred_after = client.get(f"/api/v1/tasks/{task_id}/predict")
        assert pred_after.status_code == 400

    def test_delete_and_verify_workflow(self, client):
        """Workflow: create resources, delete them, confirm they are gone."""
        # Create category and task
        cat_resp = client.post("/api/v1/categories", json={"name": "Temporary"})
        cat_id = cat_resp.json()["id"]

        task_resp = client.post("/api/v1/tasks", json={"title": "Temp task", "category_id": cat_id})
        task_id = task_resp.json()["id"]

        # Delete task first
        assert client.delete(f"/api/v1/tasks/{task_id}").status_code == 204
        assert client.get(f"/api/v1/tasks/{task_id}").status_code == 404

        # Delete category
        assert client.delete(f"/api/v1/categories/{cat_id}").status_code == 204
        assert client.get("/api/v1/categories").json() == []

    def test_cumulative_badges_across_completions(self, client):
        """Workflow: complete 10 tasks and verify progressive badge earning."""
        all_new_badges = []
        for i in range(10):
            create_resp = client.post("/api/v1/tasks", json={"title": f"Task {i+1}", "priority": 2})
            task_id = create_resp.json()["id"]
            complete_resp = client.post(f"/api/v1/tasks/{task_id}/complete")
            new_badges = complete_resp.json()["new_badges"]
            all_new_badges.extend([b["name"] for b in new_badges])

        # After 10 completions, should have earned at least First Step and Getting Rolling
        assert "First Step" in all_new_badges
        assert "Getting Rolling" in all_new_badges

        # Verify via badges endpoint
        badges = client.get("/api/v1/badges").json()
        first_step = next(b for b in badges if b["name"] == "First Step")
        getting_rolling = next(b for b in badges if b["name"] == "Getting Rolling")
        assert first_step["earned"] is True
        assert getting_rolling["earned"] is True

        # Verify stats
        stats = client.get("/api/v1/stats").json()
        assert stats["tasks_completed"] == 10
        assert stats["total_points"] > 0
