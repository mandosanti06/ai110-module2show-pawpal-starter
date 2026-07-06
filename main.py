from datetime import date, time

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


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
for task in scheduler.sort_by_time():
    print(f"- {task.time}: {task.pet.name} {task.title}")

print("Nina Pending Tasks")
for task in scheduler.filter_tasks(status="pending", pet_name="Nina"):
    print(f"- {task.title} ({task.status})")

print("Schedule Warnings")
for warning in scheduler.conflict_warnings():
    print(f"- {warning}")

plan = scheduler.build_daily_plan()

print("Today's Schedule")
for item in plan.items:
    print(f"- {item.task.pet.name}: {item.describe()}")
