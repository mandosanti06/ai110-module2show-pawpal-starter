from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Owner:
    name: str
    preferences: list[str] = field(default_factory=list)

    def update_name(self, name: str) -> None:
        raise NotImplementedError

    def add_preference(self, preference: str) -> None:
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
    priority: str
    category: str

    def update_task(
        self,
        title: str,
        duration_minutes: int,
        priority: str,
        category: str,
    ) -> None:
        raise NotImplementedError

    def is_high_priority(self) -> bool:
        raise NotImplementedError


@dataclass
class ScheduleItem:
    task: Task
    start_time: str
    end_time: str
    rationale: str

    def describe(self) -> str:
        raise NotImplementedError


@dataclass
class DailyPlan:
    owner: Owner
    pet: Pet
    available_minutes: int
    items: list[ScheduleItem] = field(default_factory=list)

    def add_item(self, item: ScheduleItem) -> None:
        raise NotImplementedError

    def remaining_minutes(self) -> int:
        raise NotImplementedError

    def summary(self) -> str:
        raise NotImplementedError


@dataclass
class Scheduler:
    owner: Owner
    pet: Pet
    tasks: list[Task]
    available_minutes: int

    def prioritize_tasks(self) -> list[Task]:
        raise NotImplementedError

    def build_daily_plan(self) -> DailyPlan:
        raise NotImplementedError

    def explain_plan(self, plan: DailyPlan) -> str:
        raise NotImplementedError