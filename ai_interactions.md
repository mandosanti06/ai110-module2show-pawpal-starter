# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

### Challenge Pass: Persistence, Priority Scheduling, and Output Formatting

**Files modified**

- `pawpal_system.py`
- `app.py`
- `main.py`
- `tests/test_pawpal.py`
- `README.md`
- `ai_interactions.md`

**What I asked the agent to do**

I asked Codex to use a subagent, inspect whether the challenge requirements were already complete, and implement only missing work for advanced scheduling, JSON persistence, priority scheduling, and professional CLI/UI output.

**What the agent completed**

- Used a read-only explorer subagent to check the existing scheduler and docs.
- Confirmed the existing code already had advanced scheduling behaviors such as next-available placement, conflict handling, recurrence, spacing, preferences, and unscheduled reasons.
- Added `Owner.save_to_json()` and `Owner.load_from_json()` with custom dictionary conversion so pets and tasks persist through `data.json`.
- Restored saved `Task.pet` object references during load.
- Updated Streamlit startup to load `data.json` and save profile/task changes.
- Updated scheduling priority so `Scheduler.prioritize_tasks()` sorts by priority first, then time.
- Added plain-text CLI tables and priority markers in `main.py`.
- Added regression tests for JSON persistence and priority-before-time scheduling.
- Updated `README.md` with persistence workflow, modified files, and CLI output examples.

**Manual corrections**

- No external serialization library was added. Custom dictionary conversion was kept because the saved object graph is small.
- The existing advanced scheduling features were not rewritten after the subagent confirmed they were already present.

**What task did you give the agent?**

I used ChatGPT and Codex as AI collaborators across the project. The main
agent-style tasks were:

- Build the PawPal+ system from the starter files and UML direction.
- Review and improve the architecture so the scheduler could support priorities,
  multiple pets, fixed-time tasks, recurrence, conflicts, and unscheduled
  explanations.
- Wire the backend logic into the Streamlit app.
- Add and run tests for the scheduler.
- Use `DESIGN.md` to refactor the UI, check it with screenshots, fix visible UI
  problems, update the README with new UI images, and fill out
  `reflection.md` using evidence from the git history.

**What did the agent do?**

- In the early design commits, the agent helped turn the starter app into a
  real system design:
  - `0941ec9` / `f1875d0`: added class skeletons from the UML.
  - `844a878`: updated the UML and system design to use enums, multiple pets,
    and conflict detection.
  - `8ffaf31`: addressed a Codex review by fixing the UML path and preserving
    unscheduled reasons.
- In the core implementation commits, the agent helped build and revise the
  scheduler:
  - `5dbf72e`: implemented the main PawPal logic layer.
  - `a373607`: added quick tests.
  - `b102841`: refactored task completion from a status string to a completed
    boolean with a public `status` property.
  - `7bad0b2`: documented and reflected on the implementation.
- In the UI/backend integration commits, the agent helped connect the Streamlit
  demo to the scheduling logic:
  - `b065ebc`: established the app/backend connection.
  - `3a49d7b`: added Streamlit session-state memory.
  - `6507b47`: wired UI actions to backend logic.
- In the algorithmic-layer commits, the agent helped add scheduling features
  one small behavior at a time:
  - `8e3458c`: sorting tasks by time.
  - `aecaa96`: filtering tasks by pet and status.
  - `eac37ea`: recurring task handling.
  - `c1b70f6`: basic conflict detection.
  - `9bcb141`: sorting the final schedule by start time.
  - `61345d6`: shortest-task tiebreaker.
  - `90f6912`: pet-specific food/exercise spacing.
  - `0ecfd24`: deadline sorting.
  - `f889dcf`: category balance guard.
  - `1a3606a`: owner preference scoring.
  - `cb48419`: duplicate task detection.
  - `6a7ac2c`: retrying flexible tasks in the next open slot.
  - `a53e10d`: max daily minutes per pet.
  - `7a3e3da`: scheduled-task rationale.
  - `5431a7b`, `d3d18a0`, `c5791da`, `9fc57b3`: recurring-task automation,
    conflict handling, evaluation/refinement, and documentation.
- In the testing commits, the agent helped plan and expand verification:
  - `47f8fec`: planned core behaviors and edge cases to test.
  - `2f8f7dc`: built the automated test suite.
  - `507454b`: ran and debugged tests.
  - `af275d2`: added the automated test suite to the main project history.
- In the final documentation/UI commits and current working changes, the agent:
  - `f122f78`: reflected the algorithmic layer in the UI.
  - `a89c271`: finalized the system architecture/UML.
  - `4624c32`: polished the README and added screenshots.
  - Read `DESIGN.md`, `app.py`, `README.md`, `reflection.md`, and git history.
  - Refactored `app.py` with the RawBlock design direction: black and white
    palette, square controls, thick borders, uppercase labels/buttons, table
    styling, alert styling, and mobile-friendly spacing.
  - Used Playwright screenshots to verify desktop and mobile UI states.
  - Fixed thin Streamlit dividers, hidden button text, pale alert text, and
    low-contrast number-input controls found during screenshot review.
  - Generated `docs/screenshots/rawblock-main-input.png`,
    `docs/screenshots/rawblock-task-preview.png`,
    `docs/screenshots/rawblock-generated-schedule.png`, and
    `docs/screenshots/rawblock-mobile.png`.
  - Updated `README.md` and filled `reflection.md` section 4 from git history.
  - Ran `python3 -m pytest`,
    `PYTHONPYCACHEPREFIX=.pycache python3 -m py_compile app.py pawpal_system.py`,
    and Playwright screenshot checks with zero console errors or warnings.

**Which chats or prompts from this repo shaped the work?**

The repo does not include full chat transcripts, so I documented the concrete
chat goals that are visible from the files and commit history:

- "Check that the code you wrote is maintainable and easy to understand."
- Architecture review chats that led to `Priority(IntEnum)`, real
  `datetime.time` values, `Owner.pets`, `Task.pet`, recurrence fields,
  fixed-start tasks, and `DailyPlan.unscheduled`.
- Implementation chats that turned the UML into `pawpal_system.py` classes and
  then connected those classes to `app.py`.
- Testing chats that moved from a testing plan to automated tests for sorting,
  recurrence, conflict handling, spacing, due dates, over-budget tasks, and
  empty schedules.
- UI polish chats that used `DESIGN.md` as the source of truth, then verified
  the result with screenshots instead of trusting the CSS edit blindly.

**What did you have to verify or fix manually?**

- I had to read the generated code and make sure it matched the assignment
  instead of accepting broad AI feature ideas automatically.
- Some AI feature recommendations were too creative or not necessary for the
  project, so I kept the implementation focused on the required scheduler,
  tests, UI, and documentation.
- I verified the backend with tests because scheduler bugs can be hidden by a
  working-looking UI.
- I reviewed screenshots manually because visual quality cannot be proven by
  passing tests alone.
- The final screenshot pass revealed UI problems the agent had to fix:
  Streamlit's gray dividers did not match RawBlock, some button text disappeared
  on black backgrounds, success alert text was too pale, and number stepper
  controls had weak contrast.
- The generated schedule screenshot initially captured the wrong part of the
  page, so the agent adjusted the Playwright scroll behavior and recaptured it.
- I checked the reflection against `git log` / `git show` so the testing section
  used real commit evidence instead of vague claims.

---
