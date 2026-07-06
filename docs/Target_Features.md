# Target Features

## Core Scheduling Features

- [X] Sorting tasks by time
- [x] Filtering by pet/status
- [x] Handling recurring tasks
- [x] Basic conflict detection

## Small Logic Improvements

- [x] Sort the final schedule by `start_time` before display.
- [x] Use shortest-task-first as a tiebreaker for flexible low-priority tasks.
- [x] Add pet-specific spacing rules, such as avoiding food immediately before a walk.
- [x] Add task deadlines, then sort urgent tasks by earliest deadline after priority.
- [x] Balance task categories so one category does not use all available time.
- [x] Score tasks with owner preferences, such as boosting morning walks.
- [x] Detect duplicate daily tasks for the same pet, title, and category.
- [x] Try the next open slot for flexible tasks before marking them unscheduled.
- [x] Add a maximum daily minutes limit per pet.
- [x] Record why each scheduled task was selected.
