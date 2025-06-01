import streamlit as st


# --- Safe Setup ---
def initialize_session():
    if "habits" not in st.session_state:
        st.session_state.habits = {
            "Wake up at 5:30 AM": 74,
            "Morning Walk": 82,
            "Cold Shower": 71,
            "No Sugar": 82
        }
    if "keys" not in st.session_state:
        st.session_state.keys = list(st.session_state.habits.keys())
    if "index" not in st.session_state:
        st.session_state.index = 0

initialize_session()

# --- Logic

if st.session_state.keys:
    current_habit = st.session_state.keys[st.session_state.index]

    st.markdown(f"### Did you do **{current_habit}** today?")

    col1, col2 = st.columns(2)
    if col1.button("✅ Yes"):
        st.session_state.habits[current_habit] = min(100, st.session_state.habits[current_habit] + 1)
        st.session_state.index = (st.session_state.index + 1) % len(st.session_state.keys)
    elif col2.button("❌ No"):
        st.session_state.habits[current_habit] = max(0, st.session_state.habits[current_habit] - 1)
        st.session_state.index = (st.session_state.index + 1) % len(st.session_state.keys)
else:
    st.markdown("⚠️ No habits found.")

# --- Habit Progress Display
for habit, percent in st.session_state.habits.items():
    st.markdown(f"**{habit}** — {percent}%")
    st.progress(percent / 100)

st.markdown("---")
st.button("🟣 Situational Stuff")
