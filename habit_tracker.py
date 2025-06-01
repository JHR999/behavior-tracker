import pandas as pd
import streamlit as st
from datetime import datetime, date, time

# --- Dynamic Table for Editing Behaviors ---
@st.cache_data
def load_csv():
    return pd.read_csv("Behavior Tracking - Sheet1.csv")

df = load_csv()

# Insert Prompt Time column if not present, only for non-situational categories
if "Prompt Time" not in df.columns:
    df["Prompt Time"] = df["Category"].apply(lambda x: "08:00" if str(x).lower() != "situational" else "")
    df.to_csv("Behavior Tracking - Sheet1.csv", index=False)

today_str = date.today().isoformat()
if "daily_responses" not in st.session_state or st.session_state.get("last_checked") != today_str:
    st.session_state.daily_responses = {}
    st.session_state.last_checked = today_str

if "updated_df" not in st.session_state:
    st.session_state.updated_df = df.copy()

edited_df = st.data_editor(st.session_state.updated_df, num_rows="dynamic", use_container_width=True)

# --- Daily Behavior Check-In ---
st.markdown("---")
st.header("Daily Behavior Check-In")

for i, row in edited_df.iterrows():
    behavior = row["Behavior"]
    percent = row["Probability"]

    scheduled_time_str = row.get("Prompt Time", "00:00")
    try:
        scheduled_time = datetime.strptime(scheduled_time_str, "%H:%M").time()
    except ValueError:
        scheduled_time = time(0, 0)

    now = datetime.now().time()
    answered = st.session_state.daily_responses.get(behavior, False)

    st.markdown(f"**{behavior}** — {percent}%")
    if now >= scheduled_time and not answered:
        col1, col2 = st.columns(2)
        if col1.button(f"✅ Did '{behavior}'", key=f"yes_{i}"):
            st.session_state.updated_df.at[i, "Probability"] = min(99, max(1, percent + 1))
            st.session_state.updated_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)
            st.session_state.daily_responses[behavior] = True
            st.rerun()
        if col2.button(f"❌ Didn't Do '{behavior}'", key=f"no_{i}"):
            st.session_state.updated_df.at[i, "Probability"] = min(99, max(1, percent - 1))
            st.session_state.updated_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)
            st.session_state.daily_responses[behavior] = True
            st.rerun()
    elif answered:
        st.markdown("_✅ Already answered today_")
    else:
        st.markdown("_⏳ Waiting for scheduled time..._")