from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
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
        raise NotImplementedError

    def add_preference(self, preference: str) -> None:
        raise NotImplementedError

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    notes: str

    def update_profile(self, name: str, species: str, breed: str, notes: str) -> None:
        raise NotImplementedError


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

    def update_task(
        self,
        title: str,
        duration_minutes: int,
        priority: Priority,
        category: str,
    ) -> None:
        raise NotImplementedError

    def is_high_priority(self) -> bool:
        raise NotImplementedError

    def applies_on(self, day: date) -> bool:
        """Does this (possibly recurring) task run on `day`?"""
        raise NotImplementedError

    def is_anchored(self) -> bool:
        """True if the task must start at `fixed_start`."""
        raise NotImplementedError


@dataclass
class ScheduleItem:
    task: Task
    start_time: time  # was str — needed to compute overlaps
    end_time: time
    rationale: str

    def describe(self) -> str:
        raise NotImplementedError

    def overlaps(self, other: ScheduleItem) -> bool:
        """Do these two scheduled slots collide in time?"""
        raise NotImplementedError


@dataclass
class DailyPlan:
    owner: Owner
    day: date  # which day this plan covers (drives recurrence filtering)
    available_minutes: int
    items: list[ScheduleItem] = field(default_factory=list)
    unscheduled: list[Task] = field(default_factory=list)  # dropped tasks + why (B6)

    def add_item(self, item: ScheduleItem) -> None:
        raise NotImplementedError

    def add_unscheduled(self, task: Task, reason: str) -> None:
        """Record a task that didn't fit, so the plan can explain the gap."""
        raise NotImplementedError

    def remaining_minutes(self) -> int:
        raise NotImplementedError

    def has_conflicts(self) -> bool:
        """True if any two scheduled items overlap in time."""
        raise NotImplementedError

    def summary(self) -> str:
        raise NotImplementedError


@dataclass
class Scheduler:
    owner: Owner  # pets reached via owner.pets — no single-pet binding
    tasks: list[Task]
    available_minutes: int
    day: date

    def prioritize_tasks(self) -> list[Task]:
        raise NotImplementedError

    def build_daily_plan(self) -> DailyPlan:
        raise NotImplementedError

    def explain_plan(self, plan: DailyPlan) -> str:
        raise NotImplementedError


if __name__ == "__main__":
    # Guards the B1 fix: priority must sort by rank, not alphabetically.
    ranks = sorted([Priority.HIGH, Priority.LOW, Priority.MEDIUM])
    assert ranks == [Priority.LOW, Priority.MEDIUM, Priority.HIGH], ranks
    assert Priority.HIGH > Priority.LOW
    print("ok: priorities sort by rank")
