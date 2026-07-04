from pawpal_system import Pet, Priority, Task


def test_mark_complete_changes_task_status():
    pet = Pet("Mochi", "dog", "mixed", "")
    task = Task("Morning walk", 20, Priority.HIGH, "exercise", pet)

    task.mark_complete()

    assert task.status == "complete"


def test_adding_task_to_pet_increases_task_count():
    pet = Pet("Mochi", "dog", "mixed", "")
    task = Task("Morning walk", 20, Priority.HIGH, "exercise", pet)

    before = len(pet.tasks)
    pet.add_task(task)

    assert len(pet.tasks) == before + 1
