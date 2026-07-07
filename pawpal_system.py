from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum, IntEnum
from pathlib import Path
from typing import Any

ANCHOR_DATE = date(2000, 1, 1)
FOOD_EXERCISE_SPACING_MINUTES = 30


class Priority(IntEnum):
    # ponytail: IntEnum, not str. The whole app sorts tasks by priority, and
    # "high" < "low" < "medium" alphabetically — a str sort ranks backwards.
    # Ranks sort correctly and still print via .name.
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Recurrence(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Owner:
    name: str
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)  # was 1:1 — owners can have pet(s)

    def update_name(self, name: str) -> None:
        """Update the owner's display name."""
        self.name = name

    def add_preference(self, preference: str) -> None:
        """Add one owner preference."""
        self.preferences.append(preference)

    def add_pet(self, pet: Pet) -> None:
        """Attach a pet to this owner."""
        self.pets.append(pet)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe representation of this owner and its pets."""
        return {
            "name": self.name,
            "preferences": self.preferences,
            "pets": [pet.to_dict() for pet in self.pets],
        }

    def save_to_json(self, path: str | Path = "data.json") -> None:
        """Persist this owner, pets, and tasks to a JSON file."""
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_from_json(cls, path: str | Path = "data.json") -> Owner:
        """Load an owner, pets, and tasks from a JSON file."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        owner = cls(data["name"], list(data.get("preferences", [])))
        for pet_data in data.get("pets", []):
            pet = Pet.from_dict(pet_data)
            owner.add_pet(pet)
            for task_data in pet_data.get("tasks", []):
                pet.add_task(Task.from_dict(task_data, pet))
        return owner

@dataclass
class Pet:
    name: str
    species: str
    breed: str
    notes: str
    tasks: list[Task] = field(default_factory=list)

    def update_profile(self, name: str, species: str, breed: str, notes: str) -> None:
        """Replace the pet's profile details."""
        self.name = name
        self.species = species
        self.breed = breed
        self.notes = notes

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe representation of this pet and its tasks."""
        return {
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "notes": self.notes,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Pet:
        """Create a pet from saved JSON data."""
        return cls(
            data["name"],
            data["species"],
            data.get("breed", ""),
            data.get("notes", ""),
        )


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    category: str
    pet: Pet  # which pet this task is for — was missing, blocks multi-pet plans
    recurrence: Recurrence = Recurrence.ONCE
    weekday: int | None = None  # ponytail: 0=Mon..6=Sun; only WEEKLY needs it
    fixed_start: time | None = None  # anchored tasks (meds @ 08:00); None = flexible
    deadline: time | None = None
    due_date: date | None = None
    completed: bool = False

    def mark_complete(self, completed_on: date | None = None) -> Task | None:
        """Mark this task complete and return the next recurring task, if any.

        Daily tasks roll forward by one day. Weekly tasks roll forward by seven
        days. One-time tasks return `None`.
        """
        self.completed = True
        next_task = self.next_occurrence(completed_on or date.today())
        if next_task is not None:
            self.pet.add_task(next_task)
        return next_task

    def next_occurrence(self, completed_on: date) -> Task | None:
        """Clone this recurring task with the next due date."""
        if self.recurrence == Recurrence.DAILY:
            next_due = completed_on + timedelta(days=1)
        elif self.recurrence == Recurrence.WEEKLY:
            next_due = completed_on + timedelta(days=7)
        else:
            return None

        return Task(
            self.title,
            self.duration_minutes,
            self.priority,
            self.category,
            self.pet,
            self.recurrence,
            self.weekday if self.recurrence == Recurrence.WEEKLY else None,
            self.fixed_start,
            self.deadline,
            next_due,
        )

    @property
    def status(self) -> str:
        """Return the task's completion status."""
        return "complete" if self.completed else "pending"

    @status.setter
    def status(self, value: str) -> None:
        """Set completion from a status string."""
        self.completed = value == "complete"

    def update_task(
        self,
        title: str,
        duration_minutes: int,
        priority: Priority,
        category: str,
    ) -> None:
        """Replace editable task details."""
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category

    def is_high_priority(self) -> bool:
        """Return whether this task is high priority."""
        return self.priority == Priority.HIGH

    def applies_on(self, day: date) -> bool:
        """Return whether this task should be considered for `day`."""
        if self.due_date is not None:
            return self.due_date == day
        if self.recurrence == Recurrence.DAILY:
            return True
        if self.recurrence == Recurrence.WEEKLY:
            return self.weekday == day.weekday()
        return True

    def is_anchored(self) -> bool:
        """True if the task must start at `fixed_start`."""
        return self.fixed_start is not None

    @property
    def time(self) -> str:
        """Return the task's sortable HH:MM time string."""
        return self.fixed_start.strftime("%H:%M") if self.fixed_start else "99:99"

    @property
    def deadline_time(self) -> str:
        """Return the task's sortable deadline string."""
        return self.deadline.strftime("%H:%M") if self.deadline else "99:99"

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe representation of this task."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority.name,
            "category": self.category,
            "recurrence": self.recurrence.value,
            "weekday": self.weekday,
            "fixed_start": _time_to_json(self.fixed_start),
            "deadline": _time_to_json(self.deadline),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], pet: Pet) -> Task:
        """Create a task from saved JSON data and reattach it to a pet."""
        return cls(
            data["title"],
            int(data["duration_minutes"]),
            Priority[data.get("priority", "MEDIUM")],
            data.get("category", "care"),
            pet,
            Recurrence(data.get("recurrence", Recurrence.ONCE.value)),
            data.get("weekday"),
            _time_from_json(data.get("fixed_start")),
            _time_from_json(data.get("deadline")),
            date.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            bool(data.get("completed", False)),
        )

@dataclass
class ScheduleItem:
    task: Task
    start_time: time  # was str — needed to compute overlaps
    end_time: time
    rationale: str

    def describe(self) -> str:
        """Return a human-readable scheduled item description."""
        return (
            f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}: "
            f"{self.task.title} ({self.rationale})"
        )

    def overlaps(self, other: ScheduleItem) -> bool:
        """Return whether two half-open time ranges overlap."""
        return self.start_time < other.end_time and other.start_time < self.end_time


@dataclass
class UnscheduledTask:
    # Keeps the "why" with the task so summary()/explain_plan() can show the gap.
    task: Task
    reason: str

@dataclass
class DailyPlan:
    owner: Owner
    day: date  # which day this plan covers (drives recurrence filtering)
    available_minutes: int
    items: list[ScheduleItem] = field(default_factory=list)
    unscheduled: list[UnscheduledTask] = field(default_factory=list)  # dropped + why (B6)

    def add_item(self, item: ScheduleItem) -> None:
        """Add a scheduled item to the plan."""
        self.items.append(item)

    def add_unscheduled(self, task: Task, reason: str) -> None:
        """Record a task that didn't fit, so the plan can explain the gap."""
        self.unscheduled.append(UnscheduledTask(task, reason))

    def remaining_minutes(self) -> int:
        """Return the day's remaining time budget in minutes."""
        used = sum(item.task.duration_minutes for item in self.items)
        return self.available_minutes - used

    def has_conflicts(self) -> bool:
        """Return whether any pair of scheduled items overlaps."""
        for index, item in enumerate(self.items):
            if any(item.overlaps(other) for other in self.items[index + 1 :]):
                return True
        return False

    def summary(self) -> str:
        """Return a readable summary of scheduled and unscheduled tasks."""
        scheduled = ", ".join(item.describe() for item in self.items) or "No scheduled tasks"
        unscheduled = ", ".join(
            f"{item.task.title} ({item.reason})" for item in self.unscheduled
        )
        if unscheduled:
            scheduled += f"; Unscheduled: {unscheduled}"
        return scheduled


@dataclass
class Scheduler:
    owner: Owner  # pets reached via owner.pets — no single-pet binding
    tasks: list[Task]
    available_minutes: int
    day: date
    max_minutes_per_pet: int | None = None

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks ordered by fixed start time, with flexible tasks last."""
        return sorted(tasks or self.tasks, key=lambda task: task.time)

    def filter_tasks(
        self,
        status: str | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Return tasks matching optional completion status and pet name filters."""
        return [
            task
            for task in self.tasks
            if (status is None or task.status == status)
            and (pet_name is None or task.pet.name == pet_name)
        ]

    def complete_task(self, task: Task, completed_on: date | None = None) -> Task | None:
        """Complete a task and append its next recurring instance to this scheduler."""
        next_task = task.mark_complete(completed_on or self.day)
        if next_task is not None and next_task not in self.tasks:
            self.tasks.append(next_task)
        return next_task

    def conflict_warnings(self, tasks: list[Task] | None = None) -> list[str]:
        """Return warnings for fixed-start tasks that share the same time."""
        by_time: dict[str, list[Task]] = {}
        for task in tasks or self.tasks:
            if task.fixed_start is None:
                continue
            by_time.setdefault(task.time, []).append(task)

        warnings = []
        for start, matches in sorted(by_time.items()):
            if len(matches) < 2:
                continue
            names = ", ".join(f"{task.pet.name} {task.title}" for task in matches)
            warnings.append(f"Warning: {start} has overlapping tasks: {names}")
        return warnings

    def tasks_for_day(self) -> list[Task]:
        """Return unique, incomplete owner tasks that apply on this scheduler's day."""
        tasks = []
        seen = set()
        for task in self.tasks:
            if task.pet not in self.owner.pets or not task.applies_on(self.day) or task.completed:
                continue
            key = (task.pet.name, task.title, task.category, task.recurrence)
            if key in seen:
                continue
            seen.add(key)
            tasks.append(task)
        return tasks

    def has_conflict(self, item: ScheduleItem, items: list[ScheduleItem]) -> bool:
        """Return whether one scheduled item overlaps any existing scheduled item."""
        return any(item.overlaps(existing) for existing in items)

    def violates_pet_spacing(self, item: ScheduleItem, items: list[ScheduleItem]) -> bool:
        """Return whether food and exercise are too close for the same pet."""
        for existing in items:
            if item.task.pet != existing.task.pet:
                continue
            categories = {item.task.category, existing.task.category}
            if categories == {"food", "exercise"} and _gap_minutes(item, existing) < FOOD_EXERCISE_SPACING_MINUTES:
                return True
        return False

    def would_monopolize_category(
        self,
        task: Task,
        plan: DailyPlan,
        daily_categories: set[str],
    ) -> bool:
        """Return whether adding this task would spend all time on one category."""
        category_minutes = sum(
            item.task.duration_minutes for item in plan.items if item.task.category == task.category
        )
        has_other_category = any(category != task.category for category in daily_categories)
        return has_other_category and category_minutes + task.duration_minutes >= plan.available_minutes

    def exceeds_pet_minutes(self, task: Task, plan: DailyPlan) -> bool:
        """Return whether adding this task would exceed the pet's daily limit."""
        if self.max_minutes_per_pet is None:
            return False
        pet_minutes = sum(
            item.task.duration_minutes for item in plan.items if item.task.pet == task.pet
        )
        return pet_minutes + task.duration_minutes > self.max_minutes_per_pet

    def selection_rationale(self, task: Task, placement: str) -> str:
        """Build the human-readable reason shown for a scheduled task."""
        parts = [placement, f"{task.priority.name.lower()} priority"]
        if self.preference_score(task):
            parts.append("matches owner preference")
        if task.deadline:
            parts.append(f"deadline {task.deadline_time}")
        return ", ".join(parts)

    def preference_score(self, task: Task) -> int:
        """Return how many owner preference tokens match this task."""
        text = f"{task.title} {task.category} {task.pet.notes}".lower()
        return sum(token in text for token in self.preference_tokens())

    def preference_tokens(self) -> list[str]:
        """Return normalized owner preference words used for simple scoring."""
        return [
            token.rstrip("s")
            for preference in self.owner.preferences
            for token in preference.lower().split()
        ]

    def task_sort_key(self, task: Task) -> tuple[int, str, bool, str, int, int]:
        """Return the scheduler's priority tuple for one task."""
        return (
            -task.priority,
            task.time,
            not task.is_anchored(),
            task.deadline_time,
            -self.preference_score(task),
            task.duration_minutes,
        )

    def prioritize_tasks(self) -> list[Task]:
        """Return today's tasks ordered by priority, time, deadline, preference, and duration."""
        return sorted(
            self.tasks_for_day(),
            key=self.task_sort_key,
        )

    def build_daily_plan(self) -> DailyPlan:
        """Build a conflict-checked daily schedule from prioritized tasks."""
        plan = DailyPlan(self.owner, self.day, self.available_minutes)
        next_start = time(9, 0)
        daily_categories = {task.category for task in self.tasks_for_day()}

        for task in self.prioritize_tasks():
            if task.duration_minutes > plan.remaining_minutes():
                plan.add_unscheduled(task, "not enough available minutes")
                continue

            if self.would_monopolize_category(task, plan, daily_categories):
                plan.add_unscheduled(task, "category would use all available time")
                continue

            if self.exceeds_pet_minutes(task, plan):
                plan.add_unscheduled(task, "pet daily limit reached")
                continue

            start = (
                task.fixed_start
                if task.fixed_start is not None
                else _first_available_start(next_start, task.duration_minutes, plan.items)
            )
            end = _add_minutes(start, task.duration_minutes)
            placement = "fixed start" if task.is_anchored() else "next available"
            item = ScheduleItem(task, start, end, self.selection_rationale(task, placement))

            if self.has_conflict(item, plan.items):
                if not task.is_anchored():
                    start = _first_available_start(end, task.duration_minutes, plan.items)
                    end = _add_minutes(start, task.duration_minutes)
                    item = ScheduleItem(task, start, end, self.selection_rationale(task, "next open slot"))
                if self.has_conflict(item, plan.items):
                    plan.add_unscheduled(task, "conflicts with scheduled task")
                    continue

            if self.violates_pet_spacing(item, plan.items):
                plan.add_unscheduled(task, "too close to food or exercise")
                continue

            plan.add_item(item)
            if not task.is_anchored():
                next_start = end

        plan.items.sort(key=lambda item: item.start_time)
        return plan

    def explain_plan(self, plan: DailyPlan) -> str:
        """Return the plan's explanation text."""
        return plan.summary()


def _add_minutes(start: time, minutes: int) -> time:
    """Return a time offset by `minutes` from `start`."""
    return (datetime.combine(ANCHOR_DATE, start) + timedelta(minutes=minutes)).time()


def _first_available_start(start: time, minutes: int, items: list[ScheduleItem]) -> time:
    """Return the first non-overlapping start at or after `start`."""
    candidate = start
    for existing in sorted(items, key=lambda item: item.start_time):
        candidate_end = _add_minutes(candidate, minutes)
        if candidate < existing.end_time and existing.start_time < candidate_end:
            candidate = existing.end_time
    return candidate


def _gap_minutes(first: ScheduleItem, second: ScheduleItem) -> int:
    """Return the minutes between two non-overlapping items, or 0 if they overlap."""
    if first.end_time <= second.start_time:
        return _minutes_between(first.end_time, second.start_time)
    if second.end_time <= first.start_time:
        return _minutes_between(second.end_time, first.start_time)
    return 0


def _minutes_between(start: time, end: time) -> int:
    """Return whole minutes from `start` to `end`."""
    delta = datetime.combine(ANCHOR_DATE, end) - datetime.combine(ANCHOR_DATE, start)
    return int(delta.total_seconds() // 60)


def _time_to_json(value: time | None) -> str | None:
    """Return a JSON-safe time string."""
    return value.strftime("%H:%M") if value else None


def _time_from_json(value: str | None) -> time | None:
    """Parse a saved HH:MM time string."""
    return time.fromisoformat(value) if value else None


if __name__ == "__main__":
    # Guards the B1 fix: priority must sort by rank, not alphabetically.
    ranks = sorted([Priority.HIGH, Priority.LOW, Priority.MEDIUM])
    assert ranks == [Priority.LOW, Priority.MEDIUM, Priority.HIGH], ranks
    assert Priority.HIGH > Priority.LOW

    day = date(2026, 7, 6)  # Monday
    owner = Owner("Mando")
    dog = Pet("Nina", "dog", "mixed", "")
    cat = Pet("Milo", "cat", "tabby", "")
    other = Pet("Rex", "dog", "lab", "")
    owner.add_pet(dog)
    owner.add_pet(cat)
    owner.add_preference("morning walks")
    owner.update_name("Amanda")
    dog.update_profile("Nina", "dog", "mixed", "likes shade")

    meds = Task("Give meds", 15, Priority.HIGH, "health", dog, Recurrence.DAILY, fixed_start=time(9, 30))
    walk = Task("Walk", 30, Priority.MEDIUM, "exercise", dog)
    brush = Task("Brush", 20, Priority.LOW, "grooming", cat, Recurrence.WEEKLY, weekday=day.weekday())
    ignored = Task("Other pet", 10, Priority.HIGH, "care", other)
    conflict = Task("Breakfast", 45, Priority.HIGH, "food", dog)
    fixed_conflict = Task("Check pulse", 10, Priority.MEDIUM, "health", dog, fixed_start=time(9, 35))
    too_long = Task("Park", 90, Priority.LOW, "exercise", dog)
    done = Task("Done", 5, Priority.HIGH, "care", dog, completed=True)

    assert meds.applies_on(day)
    assert brush.applies_on(day)
    assert not Task("Sunday bath", 10, Priority.LOW, "care", dog, Recurrence.WEEKLY, weekday=6).applies_on(day)
    assert meds.is_anchored()
    assert not ScheduleItem(walk, time(9), time(9, 30), "").overlaps(
        ScheduleItem(meds, time(9, 30), time(9, 45), "")
    )
    daily_task = Task("Daily meds", 15, Priority.HIGH, "health", dog, Recurrence.DAILY)
    weekly_task = Task("Weekly brush", 20, Priority.LOW, "grooming", cat, Recurrence.WEEKLY, weekday=day.weekday())
    daily_next = daily_task.mark_complete(day)
    assert daily_next is not None
    assert daily_next.due_date == day + timedelta(days=1)
    assert daily_next.applies_on(day + timedelta(days=1))
    weekly_next = weekly_task.mark_complete(day)
    assert weekly_next is not None
    assert weekly_next.due_date == day + timedelta(days=7)

    scheduler = Scheduler(owner, [walk, meds, brush, ignored, conflict, fixed_conflict, too_long, done], 80, day)
    same_time = Task("Pulse", 10, Priority.MEDIUM, "health", dog, fixed_start=time(9, 30))
    warnings = scheduler.conflict_warnings([meds, same_time])
    assert warnings and "09:30" in warnings[0]
    plan = scheduler.build_daily_plan()
    assert [item.task.title for item in plan.items] == ["Give meds", "Breakfast", "Brush"]
    assert [item.start_time for item in plan.items] == [time(9, 30), time(9, 45), time(10, 30)]
    assert {item.task.title for item in plan.unscheduled} == {"Check pulse", "Walk", "Park"}
    assert "Done" not in {item.task.title for item in plan.items}
    assert not plan.has_conflicts()
    assert plan.remaining_minutes() == 0
    assert "Give meds" in scheduler.explain_plan(plan)
    print("ok: pawpal system self-check passed")
