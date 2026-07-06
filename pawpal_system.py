from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum, IntEnum


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
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark the task as complete."""
        self.completed = True

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
        """Does this (possibly recurring) task run on `day`?"""
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
        """Do these two scheduled slots collide in time?"""
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
        """Return unscheduled minutes still available in the plan."""
        used = sum(item.task.duration_minutes for item in self.items)
        return self.available_minutes - used

    def has_conflicts(self) -> bool:
        """True if any two scheduled items overlap in time."""
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

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks sorted by their HH:MM time string."""
        return sorted(tasks or self.tasks, key=lambda task: task.time)

    def filter_tasks(
        self,
        status: str | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Return tasks matching optional completion status and pet name."""
        return [
            task
            for task in self.tasks
            if (status is None or task.status == status)
            and (pet_name is None or task.pet.name == pet_name)
        ]

    def tasks_for_day(self) -> list[Task]:
        """Return incomplete owner tasks whose recurrence applies today."""
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
        """Return whether an item overlaps any scheduled item."""
        return any(item.overlaps(existing) for existing in items)

    def violates_pet_spacing(self, item: ScheduleItem, items: list[ScheduleItem]) -> bool:
        """Avoid scheduling food and exercise too close for the same pet."""
        for existing in items:
            if item.task.pet != existing.task.pet:
                continue
            categories = {item.task.category, existing.task.category}
            if categories == {"food", "exercise"} and _gap_minutes(item, existing) < 30:
                return True
        return False

    def would_monopolize_category(self, task: Task, plan: DailyPlan) -> bool:
        """Avoid spending the whole day on one category when others apply."""
        category_minutes = sum(
            item.task.duration_minutes for item in plan.items if item.task.category == task.category
        )
        has_other_category = any(other.category != task.category for other in self.tasks_for_day())
        return has_other_category and category_minutes + task.duration_minutes >= plan.available_minutes

    def preference_score(self, task: Task) -> int:
        """Score tasks that match owner preference words."""
        text = f"{task.title} {task.category} {task.pet.notes}".lower()
        return sum(
            token.rstrip("s") in text
            for preference in self.owner.preferences
            for token in preference.lower().split()
        )

    def task_sort_key(self, task: Task) -> tuple[bool, int, str, int, int]:
        """Anchored first, then priority, deadline, preference, duration."""
        return (
            not task.is_anchored(),
            -task.priority,
            task.deadline_time,
            -self.preference_score(task),
            task.duration_minutes,
        )

    def prioritize_tasks(self) -> list[Task]:
        """Return schedulable tasks ordered by scheduling priority."""
        return sorted(
            self.tasks_for_day(),
            key=self.task_sort_key,
        )

    def build_daily_plan(self) -> DailyPlan:
        """Build a daily plan from prioritized tasks."""
        plan = DailyPlan(self.owner, self.day, self.available_minutes)
        next_start = time(9, 0)

        for task in self.prioritize_tasks():
            if task.duration_minutes > plan.remaining_minutes():
                plan.add_unscheduled(task, "not enough available minutes")
                continue

            if self.would_monopolize_category(task, plan):
                plan.add_unscheduled(task, "category would use all available time")
                continue

            start = (
                task.fixed_start
                if task.fixed_start is not None
                else _first_available_start(next_start, task.duration_minutes, plan.items)
            )
            end = _add_minutes(start, task.duration_minutes)
            item = ScheduleItem(task, start, end, "fixed start" if task.is_anchored() else "next available")

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
    return (datetime.combine(date.today(), start) + timedelta(minutes=minutes)).time()


def _first_available_start(start: time, minutes: int, items: list[ScheduleItem]) -> time:
    candidate = start
    for existing in sorted(items, key=lambda item: item.start_time):
        candidate_item = ScheduleItem(existing.task, candidate, _add_minutes(candidate, minutes), "")
        if candidate_item.overlaps(existing):
            candidate = existing.end_time
    return candidate


def _gap_minutes(first: ScheduleItem, second: ScheduleItem) -> int:
    if first.end_time <= second.start_time:
        return _minutes_between(first.end_time, second.start_time)
    if second.end_time <= first.start_time:
        return _minutes_between(second.end_time, first.start_time)
    return 0


def _minutes_between(start: time, end: time) -> int:
    delta = datetime.combine(date.today(), end) - datetime.combine(date.today(), start)
    return int(delta.total_seconds() // 60)


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

    scheduler = Scheduler(owner, [walk, meds, brush, ignored, conflict, fixed_conflict, too_long, done], 80, day)
    plan = scheduler.build_daily_plan()
    assert [item.task.title for item in plan.items] == ["Give meds", "Breakfast", "Brush"]
    assert [item.start_time for item in plan.items] == [time(9, 30), time(9, 45), time(10, 30)]
    assert {item.task.title for item in plan.unscheduled} == {"Check pulse", "Walk", "Park"}
    assert "Done" not in {item.task.title for item in plan.items}
    assert not plan.has_conflicts()
    assert plan.remaining_minutes() == 0
    assert "Give meds" in scheduler.explain_plan(plan)
    print("ok: pawpal system self-check passed")
