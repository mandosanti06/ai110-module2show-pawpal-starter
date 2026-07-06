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
- [ ] Balance task categories so one category does not use all available time.
- [ ] Score tasks with owner preferences, such as boosting morning walks.
- [ ] Detect duplicate daily tasks for the same pet, title, and category.
- [ ] Try the next open slot for flexible tasks before marking them unscheduled.
- [ ] Add a maximum daily minutes limit per pet.
- [ ] Record why each scheduled task was selected.
