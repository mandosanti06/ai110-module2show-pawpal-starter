from datetime import date, time

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


def priority_label(priority: Priority) -> str:
    icons = {
        Priority.HIGH: "!!! High",
        Priority.MEDIUM: "!! Medium",
        Priority.LOW: "! Low",
    }
    return icons[priority]


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    widths = [
        max(len(str(value)) for value in [header, *[row[index] for row in rows]])
        for index, header in enumerate(headers)
    ]
    line = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    print(line)
    print("| " + " | ".join(header.ljust(widths[index]) for index, header in enumerate(headers)) + " |")
    print(line)
    for row in rows:
        print("| " + " | ".join(str(value).ljust(widths[index]) for index, value in enumerate(row)) + " |")
    print(line)


owner = Owner("Mando")
dog = Pet("Nina", "dog", "mixed", "likes morning walks")
cat = Pet("Milo", "cat", "tabby", "prefers quiet feeding time")

owner.add_pet(dog)
owner.add_pet(cat)

tasks = [
    Task("Brush", 15, Priority.LOW, "grooming", cat, fixed_start=time(10, 30)),
    Task("Quiet feeding", 15, Priority.MEDIUM, "food", cat, fixed_start=time(9, 0)),
    Task("Walk", 30, Priority.MEDIUM, "exercise", dog, fixed_start=time(9, 0)),
    Task("Breakfast", 20, Priority.HIGH, "food", dog, fixed_start=time(8, 0)),
]

scheduler = Scheduler(owner, tasks, available_minutes=120, day=date.today())

print("Tasks Sorted by Time")
print_table(
    ["Time", "Pet", "Task", "Priority"],
    [
        [task.time, task.pet.name, task.title, priority_label(task.priority)]
        for task in scheduler.sort_by_time()
    ],
)

print("Nina Pending Tasks")
print_table(
    ["Task", "Status"],
    [[task.title, task.status] for task in scheduler.filter_tasks(status="pending", pet_name="Nina")],
)

print("Schedule Warnings")
for warning in scheduler.conflict_warnings():
    print(f"- {warning}")

plan = scheduler.build_daily_plan()

print("Today's Schedule")
print_table(
    ["Time", "Pet", "Task", "Why scheduled"],
    [
        [
            f"{item.start_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')}",
            item.task.pet.name,
            item.task.title,
            item.rationale,
        ]
        for item in plan.items
    ],
)
