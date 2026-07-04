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
        self.name = name

    def add_preference(self, preference: str) -> None:
        self.preferences.append(preference)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

@dataclass
class Pet:
    name: str
    species: str
    breed: str
    notes: str

    def update_profile(self, name: str, species: str, breed: str, notes: str) -> None:
        self.name = name
        self.species = species
        self.breed = breed
        self.notes = notes


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
    completed: bool = False

    def update_task(
        self,
        title: str,
        duration_minutes: int,
        priority: Priority,
        category: str,
    ) -> None:
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category

    def is_high_priority(self) -> bool:
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

@dataclass
class ScheduleItem:
    task: Task
    start_time: time  # was str — needed to compute overlaps
    end_time: time
    rationale: str

    def describe(self) -> str:
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
        self.items.append(item)

    def add_unscheduled(self, task: Task, reason: str) -> None:
        """Record a task that didn't fit, so the plan can explain the gap."""
        self.unscheduled.append(UnscheduledTask(task, reason))

    def remaining_minutes(self) -> int:
        used = sum(item.task.duration_minutes for item in self.items)
        return self.available_minutes - used

    def has_conflicts(self) -> bool:
        """True if any two scheduled items overlap in time."""
        for index, item in enumerate(self.items):
            if any(item.overlaps(other) for other in self.items[index + 1 :]):
                return True
        return False

    def summary(self) -> str:
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

    def prioritize_tasks(self) -> list[Task]:
        return sorted(
            (
                task
                for task in self.tasks
                if task.pet in self.owner.pets and task.applies_on(self.day) and not task.completed
            ),
            key=lambda task: (not task.is_anchored(), -task.priority, task.duration_minutes),
        )

    def build_daily_plan(self) -> DailyPlan:
        plan = DailyPlan(self.owner, self.day, self.available_minutes)
        next_start = time(9, 0)

        for task in self.prioritize_tasks():
            if task.duration_minutes > plan.remaining_minutes():
                plan.add_unscheduled(task, "not enough available minutes")
                continue

            start = (
                task.fixed_start
                if task.fixed_start is not None
                else _first_available_start(next_start, task.duration_minutes, plan.items)
            )
            end = _add_minutes(start, task.duration_minutes)
            item = ScheduleItem(task, start, end, "fixed start" if task.is_anchored() else "next available")

            if any(item.overlaps(existing) for existing in plan.items):
                plan.add_unscheduled(task, "conflicts with scheduled task")
                continue

            plan.add_item(item)
            if not task.is_anchored():
                next_start = end

        return plan

    def explain_plan(self, plan: DailyPlan) -> str:
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
