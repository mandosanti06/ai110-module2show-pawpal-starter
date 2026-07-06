# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- My initial UML design centered on three core user actions: entering owner and pet information, adding or editing pet care tasks, and generating a daily schedule that shows what should happen today.
- I planned the classes so that one part of the system would store the pet and task data, another would handle the scheduling rules, and the Streamlit UI would collect input and display the final plan.
- The goal was to keep the design simple enough to test the scheduling logic separately from the interface.

**b. Design changes**

Reviewing the skeleton against the scenario surfaced six bottlenecks. Each fix
changed both `pawpal_system.py` and `diagrams/uml.mmd`:

- **Priority became an enum, not a string.** The scheduler's whole job is
  ranking tasks, but as a `str` they sorted alphabetically — `"high" < "low" <
  "medium"` — which is backwards. I introduced `Priority(IntEnum)` so tasks sort
  by rank. (A `__main__` self-check asserts this.)
- **Times became `datetime.time`, not strings.** The scenario asks for conflict
  handling, but you can't detect overlapping slots on strings. Real times let me
  add `ScheduleItem.overlaps()` and `DailyPlan.has_conflicts()`.
- **Supported multiple pets.** The original `Owner`–`Pet` link was one-to-one,
  the `Scheduler` was bound to a single pet, and `Task` had no way to say which
  pet it was for. I changed it to `Owner.pets: list[Pet]`, added `Task.pet`, and
  dropped the single-pet binding so one scheduler can plan a multi-pet household.
- **Added recurrence and anchored tasks.** `Task` gained `recurrence`
  (once/daily/weekly) with `applies_on(day)` so the scheduler can pick "today's"
  tasks, and `fixed_start` with `is_anchored()` so fixed-time tasks (meds at
  08:00) can be expressed — which is also what gives conflict detection
  something real to catch.
- **Plans now record skipped tasks.** When a task doesn't fit the time budget it
  goes into `DailyPlan.unscheduled` via `add_unscheduled(task, reason)` instead
  of silently disappearing, so the plan can still explain the gap.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- The lightweight warning system in `Scheduler.conflict_warnings()` only checks
  tasks with the exact same fixed start time. The deeper schedule builder still
  uses `ScheduleItem.overlaps()` for duration-based conflicts, but the warning
  pass is intentionally simpler.
- That tradeoff is reasonable here because the terminal demo needs a friendly
  warning instead of a crash, and exact-time conflicts are the easiest mistake
  for a pet owner to understand and fix quickly. A full calendar-style conflict
  report would be more complete, but it would add complexity before the app
  needs it.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
