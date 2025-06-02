import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="Habit Tracker", page_icon=":clipboard:")

st.title("Habit Tracker")

# Load or initialize habit data
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("habits.csv", parse_dates=["date"])
        data["date"] = pd.to_datetime(data["date"])
        return data
    except FileNotFoundError:
        return pd.DataFrame(columns=["date", "behavior", "completed"])

data = load_data()

# Sidebar for adding new habits
st.sidebar.header("Add New Habit")
new_habit = st.sidebar.text_input("Habit name")
if st.sidebar.button("Add Habit"):
    if new_habit:
        if new_habit not in data["behavior"].unique():
            today = pd.to_datetime(datetime.date.today())
            new_entry = pd.DataFrame({"date": [today], "behavior": [new_habit], "completed": [False]})
            data = pd.concat([data, new_entry], ignore_index=True)
            data.to_csv("habits.csv", index=False)
            st.sidebar.success(f"Habit '{new_habit}' added!")
        else:
            st.sidebar.warning("Habit already exists.")
    else:
        st.sidebar.warning("Please enter a habit name.")

# Select date to view or input data
selected_date = st.date_input("Select date", datetime.date.today())

# Display habits for the selected date
st.header(f"Habits for {selected_date.strftime('%B %d, %Y')}")

behaviors = data["behavior"].unique()
if len(behaviors) == 0:
    st.info("No habits added yet. Use the sidebar to add a new habit.")
else:
    for behavior in behaviors:
        habit_data = data[(data["behavior"] == behavior) & (data["date"] == pd.to_datetime(selected_date))]
        completed = False
        if not habit_data.empty:
            completed = bool(habit_data.iloc[0]["completed"])
        new_completed = st.checkbox(behavior, value=completed, key=f"{behavior}_{selected_date}")
        if new_completed != completed:
            if habit_data.empty:
                new_entry = pd.DataFrame({"date": [selected_date], "behavior": [behavior], "completed": [new_completed]})
                data = pd.concat([data, new_entry], ignore_index=True)
            else:
                idx = habit_data.index[0]
                data.at[idx, "completed"] = new_completed
            data.to_csv("habits.csv", index=False)

# Calculate and display completion percentage for today
today = pd.to_datetime(datetime.date.today())
today_data = data[data["date"] == today]
if not today_data.empty:
    completed_count = today_data["completed"].sum()
    total_habits = len(today_data)
    percent = int((completed_count / total_habits) * 100)
else:
    percent = 0

# Determine label based on completion percentage
label = ""
if percent < 10:
    label = "Extremely Unlikely (0–9%)"
elif percent < 20:
    label = "Very Unlikely (10–19%)"
elif percent < 40:
    label = "Unlikely (20–39%)"
elif percent < 60:
    label = "Neutral (40–59%)"
elif percent < 80:
    label = "Likely (60–79%)"
elif percent < 95:
    label = "Very Likely (80–94%)"
else:
    label = "Almost Certain (95–99%)"

st.markdown(f"""
    <div class="daily-checkin-card" style="background-color: #333; padding: 20px; border-radius: 10px; text-align: center;">
        <h2 style='font-size: 50px; color: white; margin-bottom: 10px;'>Habit Completion</h2>
        <p style='font-size: 20px; color: #ccc; margin: 0;'>{percent}% Chance</p>
        <p style='font-size: 16px; color: #888; margin-top: 4px;'>{label}</p>
    </div>
""", unsafe_allow_html=True)