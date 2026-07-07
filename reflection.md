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
  
  - ChatGPT and Codex (GPT 5.5 Mid)

- What kinds of prompts or questions were most helpful?
  - Check that the code you wrote is maintainable and easy to understand.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  - Feature recommendations where kind of bad and creative decisions.
- How did you evaluate or verify what the AI suggested?
  - By testing and by reading the code it wrote.

---

## 4. Testing and Verification

**a. What you tested**

- The git history shows testing was planned first in `47f8fec` with core
  behavior and edge-case notes, then expanded in `2f8f7dc` / `af275d2` into
  automated tests for the scheduler.
- Those tests covered task completion, adding tasks to a pet, chronological
  sorting, daily recurrence, duplicate fixed-time conflict warnings, empty
  schedules, ignoring tasks for pets outside the owner, unscheduling exact
  fixed-time conflicts, allowing adjacent time ranges, excluding weekly tasks
  on the wrong weekday, due-date filtering, food/exercise spacing, and
  over-budget tasks.
- These tests mattered because the scheduler is the part most likely to fail
  silently. If sorting, recurrence, conflict handling, or unscheduled reasons
  are wrong, the UI can still look correct while giving the pet owner a bad
  plan.
- For the final UI pass, I also verified the Streamlit app with screenshots:
  main input form, task preview, generated schedule, and mobile layout. The
  screenshot loop caught UI issues with thin dividers, hidden button text, and
  pale alert text before the README images were updated.

**b. Confidence**

- I am reasonably confident in the scheduler's core behavior because the
  history includes targeted tests for the main scheduling rules and edge cases,
  and the current verification still passes the available pytest suite.
- I would test more combinations next: multiple pets with competing high
  priority tasks, deadlines combined with fixed starts, duplicate flexible
  tasks, max-minutes-per-pet with recurring tasks, and UI flows for adding
  fixed-start tasks instead of only using the backend and CLI examples.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  - The lessons learned I tried to read almost everything the AI outputed to understand everything.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  - I would have started this project before this project took me longer than I thought.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

  - Sometimes we let AI run wild and thats not right we should know what the AI agents are doing in our code.
