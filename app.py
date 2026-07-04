from datetime import date

import streamlit as st
import pawpal_system

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
if "owner" not in st.session_state:
    st.session_state.owner = pawpal_system.Owner(owner_name)
else:
    st.session_state.owner.update_name(owner_name)

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
if "pet" not in st.session_state:
    st.session_state.pet = pawpal_system.Pet(pet_name, species, "", "")
    st.session_state.owner.add_pet(st.session_state.pet)
else:
    st.session_state.pet.update_profile(pet_name, species, "", "")

st.markdown("### Tasks")
st.caption("Add a few tasks. These feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    task = pawpal_system.Task(
        task_title,
        int(duration),
        pawpal_system.Priority[priority.upper()],
        "care",
        st.session_state.pet,
    )
    st.session_state.pet.add_task(task)
    st.session_state.tasks.append(task)

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": task.pet.name,
                "title": task.title,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority.name.lower(),
            }
            for task in st.session_state.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
available_minutes = st.number_input("Available minutes today", min_value=1, max_value=480, value=120)

if st.button("Generate schedule"):
    scheduler = pawpal_system.Scheduler(
        st.session_state.owner,
        st.session_state.tasks,
        int(available_minutes),
        date.today(),
    )
    plan = scheduler.build_daily_plan()

    st.markdown("### Today's Schedule")
    if plan.items:
        for item in plan.items:
            st.write(f"- {item.task.pet.name}: {item.describe()}")
    else:
        st.info("No scheduled tasks.")

    if plan.unscheduled:
        st.markdown("### Unscheduled")
        for item in plan.unscheduled:
            st.write(f"- {item.task.title}: {item.reason}")

    st.caption(scheduler.explain_plan(plan))
