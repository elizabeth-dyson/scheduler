
import streamlit as st
import pandas as pd
from datetime import datetime
import os
os.environ["TZ"] = "America/Chicago"
import time as _time; _time.tzset()
import json
import hashlib
import re

st.set_page_config(page_title="Liz's No-Decisions Day", layout="wide")

st.title("🚂 Liz’s No-Decisions Day Plan")
st.caption("One conveyor belt. Zero decisions. Check the box and roll.")

# ---- Define today's schedule (edit here) ----
# Format: (time_range, task)
DEFAULT_TASKS = [
    ("9:15–9:30", "Take Meds 💊"),
    ("9:30–9:45", "Dishes 🍽️"),
    ("9:45–10:00", "Vacuum 🌀"),
    ("10:00–10:30", "Litter Boxes 🐾"),
    ("10:30–11:15", "Get Drywall Anchors 🛠️"),
    ("11:15–12:00", "Hang Carpet Remnants 🐈‍⬛"),
    ("12:00–12:30", "Fill Bookshelf 📚"),
    ("12:30–13:00", "Lunch Break"),
    ("13:00–13:30", "Grocery Pickup 🛒"),
    ("13:30–14:30", "Budgeting Block 💻"),
    ("14:30–15:00", "One Name Change 📝"),
    ("15:00–15:45", "Facebook Marketplace 📱"),
    ("15:45–16:30", "Start File Cabinet 📂"),
    ("16:30–17:00", "Crochet 🧶"),
    ("17:00–17:30", "Feed Pets"),
    ("17:30–17:45", "Carpet Cleaner"),
    ("18:15–18:45", "Walk Bo"),
]

## tasks for later
# ("13:30–14:00", "Master bath clean"),
    

def normalize_task(s: str) -> str:
    s = s.lower()
    s = s.replace("–", "-")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def schedule_key(tasks):
    only_tasks = sorted([normalize_task(t[1]) for t in tasks])
    blob = json.dumps(only_tasks, ensure_ascii=False)
    return hashlib.md5(blob.encode()).hexdigest()

TODAY = datetime.now().strftime("%Y-%m-%d")
SAVE_PATH = f"progress_{TODAY}.json"
CURRENT_KEY = schedule_key(DEFAULT_TASKS)

def init_state():
    new_df = pd.DataFrame(DEFAULT_TASKS, columns=["time", "task"])
    new_df["done"] = False

    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "r") as f:
            data = json.load(f)
        
        if data.get("schedule_key") == CURRENT_KEY:
            st.session_state["tasks_df"] = pd.DataFrame(data["tasks"])
            return
        
        old_done_by_task = {}
        for t in data["tasks"]:
            old_done_by_task[normalize_task(t["task"])] = bool(t.get("done", False))
        
        new_df["done"] = [
            old_done_by_task.get(normalize_task(row.task), False)
            for row in new_df.itertuples()
        ]

    st.session_state["tasks_df"] = new_df

def persist():
    payload = {
        "date": TODAY,
        "schedule_key": CURRENT_KEY,
        "tasks": st.session_state["tasks_df"].to_dict(orient="records"),
    }
    with open(SAVE_PATH, "w") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

init_state()

df = st.session_state["tasks_df"]

# ---- Sidebar controls ----
with st.sidebar:
    st.header("Controls")
    if st.button("Reset checkboxes"):
        st.session_state["tasks_df"]["done"] = False
        persist()
        st.rerun()

    if st.button("Mark all done"):
        st.session_state["tasks_df"]["done"] = True
        persist()
        st.rerun()

    st.download_button(
        "Export as CSV",
        data=st.session_state["tasks_df"].to_csv(index=False),
        file_name="liz_schedule.csv",
        mime="text/csv",
    )

# ---- Progress ----
completed = int(df["done"].sum())
total = int(len(df))
pct = 0 if total == 0 else round(100 * completed / total)

st.subheader("Progress")
st.progress(pct / 100.0)
st.write(f"**{completed} / {total}** tasks complete (**{pct}%**).")

# ---- Highlight current slot helper ----
def is_now_in_slot(slot: str) -> bool:
    # slot like "10:00–10:20"
    try:
        slot = slot.replace("–", "-")
        start_s, end_s = [s.strip() for s in slot.split("-", 1)]
        today = datetime.now().date()
        start = datetime.combine(today, datetime.strptime(start_s, "%H:%M").time())
        end = datetime.combine(today, datetime.strptime(end_s, "%H:%M").time())
        now = datetime.now()
        return start <= now <= end
    except Exception:
        return False

# ---- Task list with checkboxes ----
st.subheader("Today’s Conveyor Belt")
for i, row in df.iterrows():
    key = f"task_{i}"
    checked = st.checkbox(f"[{row['time']}] {row['task']}", value=bool(row["done"]), key=key)
    if checked != row["done"]:
        st.session_state["tasks_df"].at[i, "done"] = checked
        persist()

    # Subtle highlight for current slot
    if is_now_in_slot(row["time"]):
        st.markdown("> **You are here →** This is the current time block.")

st.caption("Tip: Edit the DEFAULT_TASKS list in the code to change your schedule. Keep it tiny, keep it moving. 💪")
