from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, Priority, Recurrence, ScheduleItem, Scheduler, Task


DAY = date(2026, 7, 6)


def owner_with_pet() -> tuple[Owner, Pet]:
    owner = Owner("Mando")
    pet = Pet("Mochi", "dog", "mixed", "")
    owner.add_pet(pet)
    return owner, pet


def test_mark_complete_changes_task_status():
    """Completing a task should update its public status."""
    _, pet = owner_with_pet()
    task = Task("Morning walk", 20, Priority.HIGH, "exercise", pet)

    task.mark_complete()

    assert task.status == "complete"


def test_adding_task_to_pet_increases_task_count():
    """Adding a task to a pet should keep it on that pet's task list."""
    _, pet = owner_with_pet()
    task = Task("Morning walk", 20, Priority.HIGH, "exercise", pet)

    before = len(pet.tasks)
    pet.add_task(task)

    assert len(pet.tasks) == before + 1


def test_sorting_correctness_returns_tasks_in_chronological_order():
    """Sorting by time should return fixed-start tasks chronologically, with flexible tasks last."""
    owner, pet = owner_with_pet()
    noon = Task("Lunch", 10, Priority.LOW, "food", pet, fixed_start=time(12, 0))
    morning = Task("Meds", 10, Priority.HIGH, "health", pet, fixed_start=time(8, 0))
    flexible = Task("Brush", 10, Priority.MEDIUM, "grooming", pet)
    scheduler = Scheduler(owner, [noon, flexible, morning], 60, DAY)

    sorted_tasks = scheduler.sort_by_time()

    assert [task.title for task in sorted_tasks] == ["Meds", "Lunch", "Brush"]


def test_daily_recurrence_creates_task_for_following_day():
    """Completing a daily task should create a new task due the following day."""
    owner, pet = owner_with_pet()
    task = Task("Meds", 10, Priority.HIGH, "health", pet, Recurrence.DAILY)
    scheduler = Scheduler(owner, [task], 60, DAY)

    next_task = scheduler.complete_task(task, DAY)

    assert next_task is not None
    assert next_task.due_date == DAY + timedelta(days=1)
    assert next_task in scheduler.tasks


def test_conflict_detection_flags_duplicate_fixed_times():
    """Duplicate fixed-start times should produce a scheduler conflict warning."""
    owner, pet = owner_with_pet()
    meds = Task("Meds", 10, Priority.HIGH, "health", pet, fixed_start=time(8, 0))
    checkup = Task("Checkup", 15, Priority.MEDIUM, "health", pet, fixed_start=time(8, 0))
    scheduler = Scheduler(owner, [meds, checkup], 60, DAY)

    warnings = scheduler.conflict_warnings()

    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Meds" in warnings[0]
    assert "Checkup" in warnings[0]


def test_empty_pet_schedule_has_no_scheduled_tasks():
    """A pet with no tasks should build an empty plan instead of failing."""
    owner, _ = owner_with_pet()
    scheduler = Scheduler(owner, [], 60, DAY)

    plan = scheduler.build_daily_plan()

    assert plan.items == []
    assert plan.summary() == "No scheduled tasks"


def test_tasks_for_pets_outside_owner_are_ignored():
    """Tasks for pets not attached to the owner should not appear in the daily plan."""
    owner, _ = owner_with_pet()
    other_pet = Pet("Rex", "dog", "lab", "")
    task = Task("Walk Rex", 20, Priority.HIGH, "exercise", other_pet)
    scheduler = Scheduler(owner, [task], 60, DAY)

    plan = scheduler.build_daily_plan()

    assert plan.items == []
    assert plan.unscheduled == []


def test_exact_time_conflict_is_left_unscheduled():
    """When two fixed-start tasks overlap exactly, the later one should be unscheduled."""
    owner, pet = owner_with_pet()
    meds = Task("Meds", 10, Priority.HIGH, "health", pet, fixed_start=time(8, 0))
    checkup = Task("Checkup", 15, Priority.MEDIUM, "health", pet, fixed_start=time(8, 0))
    scheduler = Scheduler(owner, [meds, checkup], 60, DAY)

    plan = scheduler.build_daily_plan()

    assert [item.task.title for item in plan.items] == ["Meds"]
    assert [(item.task.title, item.reason) for item in plan.unscheduled] == [
        ("Checkup", "conflicts with scheduled task")
    ]


def test_adjacent_time_ranges_do_not_conflict():
    """Back-to-back schedule items should be allowed because their ranges do not overlap."""
    _, pet = owner_with_pet()
    walk = Task("Walk", 30, Priority.HIGH, "exercise", pet)
    meds = Task("Meds", 15, Priority.HIGH, "health", pet)
    first = ScheduleItem(walk, time(9, 0), time(9, 30), "")
    second = ScheduleItem(meds, time(9, 30), time(9, 45), "")

    assert not first.overlaps(second)


def test_wrong_weekday_recurring_task_is_excluded():
    """Weekly tasks should only apply on their configured weekday."""
    owner, pet = owner_with_pet()
    sunday_task = Task("Bath", 30, Priority.LOW, "grooming", pet, Recurrence.WEEKLY, weekday=6)
    scheduler = Scheduler(owner, [sunday_task], 60, DAY)

    assert scheduler.tasks_for_day() == []


def test_due_date_recurring_task_only_applies_on_exact_date():
    """A recurring task with a due date should only appear on that date."""
    owner, pet = owner_with_pet()
    task = Task("Meds", 10, Priority.HIGH, "health", pet, Recurrence.DAILY, due_date=DAY + timedelta(days=1))
    today_scheduler = Scheduler(owner, [task], 60, DAY)
    tomorrow_scheduler = Scheduler(owner, [task], 60, DAY + timedelta(days=1))

    assert today_scheduler.tasks_for_day() == []
    assert tomorrow_scheduler.tasks_for_day() == [task]


def test_pet_spacing_blocks_food_and_exercise_too_close_together():
    """Food and exercise for the same pet should not be scheduled less than 30 minutes apart."""
    owner, pet = owner_with_pet()
    breakfast = Task("Breakfast", 20, Priority.HIGH, "food", pet, fixed_start=time(9, 0))
    walk = Task("Walk", 20, Priority.MEDIUM, "exercise", pet, fixed_start=time(9, 25))
    scheduler = Scheduler(owner, [breakfast, walk], 60, DAY)

    plan = scheduler.build_daily_plan()

    assert [item.task.title for item in plan.items] == ["Breakfast"]
    assert [(item.task.title, item.reason) for item in plan.unscheduled] == [
        ("Walk", "too close to food or exercise")
    ]


def test_over_budget_task_is_left_unscheduled():
    """Tasks longer than the available day should be recorded as unscheduled."""
    pet = Pet("Mochi", "dog", "mixed", "")
    owner = Owner("Mando", pets=[pet])
    task = Task("Long park visit", 90, Priority.LOW, "exercise", pet)
    scheduler = Scheduler(owner, [task], 60, DAY)

    plan = scheduler.build_daily_plan()

    assert plan.items == []
    assert [(item.task.title, item.reason) for item in plan.unscheduled] == [
        ("Long park visit", "not enough available minutes")
    ]
