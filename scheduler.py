
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Liz's No-Decisions Day", layout="wide")

st.title("🚂 Liz’s No-Decisions Day Plan")
st.caption("One conveyor belt. Zero decisions. Check the box and roll.")

# ---- Define today's schedule (edit here) ----
# Format: (time_range, task)
DEFAULT_TASKS = [
    ("10:00–10:20", "Quick living room pick up + vacuum phase 1"),
    ("10:20–10:40", "Dishes"),
    ("10:40–11:00", "Laundry → switch/dry + fold one load"),
    ("11:00–11:20", "Half bath clean"),
    ("11:20–11:40", "Vacuum phase 2"),
    ("11:40–12:00", "Pay 2 credit cards"),
    ("12:00–12:30", "Financial plan (weekly saving math)"),
    ("12:30–13:00", "Walk Bo 🐾"),
    ("13:00–13:30", "Lunch"),
    ("13:30–14:00", "Master bath clean"),
    ("14:00–14:20", "Laundry → second load folded/put away"),
    ("14:20–14:40", "Vacuum phase 3"),
    ("14:40–15:00", "Fridge clean out"),
    ("15:00–15:30", "Wash bed sheets + start dryer"),
    ("15:30–16:00", "Easy name changes"),
    ("16:00–16:30", "Put stuff in new bookshelf upstairs"),
    ("16:30–17:00", "Errand → get drywall anchors"),
    ("17:00–17:30", "Hang carpet remnants for cats 🐈"),
    ("17:30–18:30", "Dinner + chill/reset"),
    ("18:30–19:30", "Project: Sunflower site OR Coffee trailer"),
    ("19:30–20:00", "Project: the other one / wrap-up"),
]

def init_state():
    if "tasks_df" not in st.session_state:
        df = pd.DataFrame(DEFAULT_TASKS, columns=["time", "task"])
        df["done"] = False
        st.session_state["tasks_df"] = df
    if "initialized_at" not in st.session_state:
        st.session_state["initialized_at"] = datetime.now()

init_state()

df = st.session_state["tasks_df"]

# ---- Sidebar controls ----
with st.sidebar:
    st.header("Controls")
    if st.button("Reset checkboxes"):
        st.session_state["tasks_df"]["done"] = False
        st.experimental_rerun()

    if st.button("Mark all done"):
        st.session_state["tasks_df"]["done"] = True
        st.experimental_rerun()

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
        start_s, end_s = slot.split("–")
        today = datetime.now().date()
        start = datetime.strptime(start_s.strip(), "%H:%M").replace(year=today.year, month=today.month, day=today.day)
        end = datetime.strptime(end_s.strip(), "%H:%M").replace(year=today.year, month=today.month, day=today.day)
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

    # Subtle highlight for current slot
    if is_now_in_slot(row["time"]):
        st.markdown("> **You are here →** This is the current time block.")

st.caption("Tip: Edit the DEFAULT_TASKS list in the code to change your schedule. Keep it tiny, keep it moving. 💪")
