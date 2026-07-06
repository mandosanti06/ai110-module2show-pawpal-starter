# Core Behaviors to Verify

1. Task sorting prioritizes fixed-start tasks first, then higher priority, earlier deadline, owner preference matches, and shorter duration.
2. Daily plans include only incomplete tasks for the owner's pets that apply on the selected day.
3. Recurring tasks create the next daily or weekly occurrence when completed.
4. Conflict detection prevents overlapping schedule items and warns when fixed-start tasks share the same time.
5. Unscheduled tasks keep a clear reason, such as not enough time, a conflict, pet spacing, category balance, or pet daily limit.

## Required Test Focus

- Sorting Correctness: Verify tasks are returned in chronological order.
- Recurrence Logic: Confirm that marking a daily task complete creates a new task for the following day.
- Conflict Detection: Verify that the Scheduler flags duplicate times.
