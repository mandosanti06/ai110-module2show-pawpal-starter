from datetime import date, time

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


owner = Owner("Mando")
dog = Pet("Nina", "dog", "mixed", "likes morning walks")
cat = Pet("Milo", "cat", "tabby", "prefers quiet feeding time")

owner.add_pet(dog)
owner.add_pet(cat)

tasks = [
    Task("Breakfast", 20, Priority.HIGH, "food", dog, fixed_start=time(8, 0)),
    Task("Walk", 30, Priority.MEDIUM, "exercise", dog, fixed_start=time(9, 0)),
    Task("Brush", 15, Priority.LOW, "grooming", cat, fixed_start=time(10, 30)),
]

plan = Scheduler(owner, tasks, available_minutes=120, day=date.today()).build_daily_plan()

print("Today's Schedule")
for item in plan.items:
    print(f"- {item.task.pet.name}: {item.describe()}")
