from datetime import date

import streamlit as st
import pawpal_system


def apply_design() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Mono&family=Work+Sans:wght@400;600;700&display=swap');

        :root {
            --black: #000000;
            --white: #FFFFFF;
            --blue: #0000FF;
            --green: #008000;
            --orange: #FFA500;
            --red: #FF0000;
            --sunken: #F0F0F0;
            --disabled: #CCCCCC;
        }

        .stApp {
            background: var(--white);
            color: var(--black);
        }

        header[data-testid="stHeader"],
        div[data-testid="stToolbar"] {
            display: none;
        }

        .block-container {
            max-width: 920px;
            padding: 40px 32px 80px;
        }

        h1, h2, h3, h4 {
            color: var(--black);
            font-family: "Archivo Black", Impact, sans-serif;
            letter-spacing: 0;
            text-transform: uppercase;
        }

        h1 {
            border-bottom: 5px solid var(--black);
            font-size: 64px;
            line-height: 1;
            margin-bottom: 16px;
            padding-bottom: 16px;
        }

        h2 {
            font-size: 48px;
            line-height: 1.05;
        }

        h3 {
            font-size: 32px;
            line-height: 1.1;
            margin-top: 0;
        }

        p, li, label, .stMarkdown, .stCaption, div[data-testid="stText"] {
            font-family: "Work Sans", Arial, sans-serif;
            letter-spacing: 0;
        }

        p, li {
            color: var(--black);
            font-size: 16px;
            line-height: 1.6;
        }

        .app-overline {
            background: var(--black);
            color: var(--white);
            display: inline-block;
            font-family: "Space Mono", monospace;
            font-size: 12px;
            letter-spacing: .1em;
            margin-bottom: 24px;
            padding: 4px 12px;
            text-transform: uppercase;
        }

        .app-lede {
            border: 3px solid var(--black);
            color: var(--black);
            font-size: 18px;
            line-height: 1.6;
            margin-bottom: 40px;
            padding: 24px;
        }

        .section-note {
            color: var(--black);
            font-family: "Space Mono", monospace;
            font-size: 14px;
            line-height: 1.5;
            margin-top: -8px;
            margin-bottom: 24px;
        }

        hr {
            background: var(--black) !important;
            border: 0 !important;
            height: 5px !important;
            margin: 40px 0 !important;
        }

        div[data-testid="stDivider"] {
            background: var(--black) !important;
            height: 5px !important;
            margin: 40px 0 !important;
        }

        div[data-testid="stDivider"] > div {
            display: none;
        }

        div[data-testid="stMarkdownContainer"] hr {
            background: var(--black) !important;
            border: 0 !important;
            height: 5px !important;
        }

        a {
            color: var(--blue);
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-baseweb="select"] > div {
            background: var(--sunken);
            border: 3px solid var(--black);
            border-radius: 0;
            box-shadow: none;
            color: var(--black);
            font-family: "Space Mono", monospace;
            font-size: 15px;
            min-height: 44px;
        }

        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stNumberInput"] input:focus {
            border: 5px solid var(--black);
            box-shadow: none;
            outline: none;
        }

        div[data-testid="stTextInput"] label,
        div[data-testid="stNumberInput"] label,
        div[data-testid="stSelectbox"] label {
            color: var(--black);
            font-family: "Archivo Black", Impact, sans-serif;
            font-size: 14px;
            letter-spacing: .1em;
            text-transform: uppercase;
        }

        .stButton > button {
            background: var(--black);
            border: 3px solid var(--black);
            border-radius: 0;
            box-shadow: none;
            color: var(--white);
            font-family: "Work Sans", Arial, sans-serif;
            font-size: 14px;
            font-weight: 700;
            letter-spacing: .12em;
            min-height: 44px;
            padding: 10px 24px;
            text-transform: uppercase;
        }

        .stButton > button:hover {
            background: var(--white);
            border-color: var(--black);
            color: var(--black);
        }

        .stButton > button:active {
            background: var(--black);
            border: 5px solid var(--black);
            color: var(--white);
        }

        .stButton > button p {
            color: inherit;
            font-size: inherit;
            font-weight: inherit;
            letter-spacing: inherit;
            line-height: 1;
            margin: 0;
            text-transform: inherit;
        }

        div[data-testid="stNumberInput"] button {
            border-left: 3px solid var(--black);
            border-radius: 0;
            color: var(--black);
        }

        div[data-testid="stAlert"] {
            background: var(--white) !important;
            border-radius: 0;
            border: 3px solid var(--black);
            box-shadow: none;
            color: var(--black);
            font-family: "Space Mono", monospace;
        }

        div[data-testid="stAlert"] * {
            color: var(--black) !important;
        }

        div[data-testid="stAlert"][kind="success"] {
            border-color: var(--green);
        }

        div[data-testid="stAlert"][kind="warning"] {
            border-color: var(--orange);
        }

        div[data-testid="stAlert"][kind="error"] {
            border-color: var(--red);
        }

        div[data-testid="stTable"] {
            border: 3px solid var(--black);
            border-radius: 0;
        }

        div[data-testid="stTable"] table {
            border-collapse: collapse;
            font-family: "Space Mono", monospace;
        }

        div[data-testid="stTable"] th {
            background: var(--black);
            color: var(--white);
            font-weight: 400;
            text-transform: uppercase;
        }

        div[data-testid="stTable"] th * {
            color: var(--white) !important;
        }

        div[data-testid="stTable"] th,
        div[data-testid="stTable"] td {
            border: 3px solid var(--black);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_intro(title: str, note: str) -> None:
    st.markdown(f"### {title}")
    st.markdown(f'<p class="section-note">{note}</p>', unsafe_allow_html=True)


def task_rows(tasks):
    return [
        {
            "Time": "Flexible" if task.fixed_start is None else task.time,
            "Pet": task.pet.name,
            "Task": task.title,
            "Minutes": task.duration_minutes,
            "Priority": task.priority.name.title(),
            "Status": task.status.title(),
        }
        for task in tasks
    ]


def schedule_rows(items):
    return [
        {
            "Time": f"{item.start_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')}",
            "Pet": item.task.pet.name,
            "Task": item.task.title,
            "Why scheduled": item.rationale,
        }
        for item in items
    ]


st.set_page_config(page_title="PawPal+", page_icon="P", layout="centered")
apply_design()

st.markdown('<div class="app-overline">Pet care planning assistant</div>', unsafe_allow_html=True)
st.title("PawPal+")
st.markdown(
    """
    <p class="app-lede">
    Plan a calm day of pet care from a short list of tasks. PawPal+ sorts pending work,
    flags fixed-time conflicts, and explains what made it onto today's schedule.
    </p>
    """,
    unsafe_allow_html=True,
)

st.divider()

section_intro("Care Profile", "Start with the owner and pet this schedule is for.")
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

st.divider()

section_intro("Tasks", "Add care tasks, then review the scheduler's sorted pending list.")

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

section_intro("Build Schedule", "Choose the time available today and generate a schedule with rationale.")
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
