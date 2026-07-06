# Target Features

## Core Scheduling Features

- [X] Sorting tasks by time
- [X] Filtering by pet/status
- [X] Handling recurring tasks
- [X] Basic conflict detection

## Small Logic Improvements

- [X] Sort the final schedule by `start_time` before display.
- [X] Use shortest-task-first as a tiebreaker for flexible low-priority tasks.
- [X] Add pet-specific spacing rules, such as avoiding food immediately before a walk.
- [X] Add task deadlines, then sort urgent tasks by earliest deadline after priority.
- [X] Balance task categories so one category does not use all available time.
- [X] Score tasks with owner preferences, such as boosting morning walks.
- [X] Detect duplicate daily tasks for the same pet, title, and category.
- [X] Try the next open slot for flexible tasks before marking them unscheduled.
- [X] Add a maximum daily minutes limit per pet.
- [X] Record why each scheduled task was selected.
