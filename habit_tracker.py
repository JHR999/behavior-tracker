import pandas as pd
import streamlit as st
from datetime import datetime, date, time

# --- Dynamic Table for Editing Behaviors ---
def load_csv():
    return pd.read_csv("Behavior Tracking - Sheet1.csv")

df = load_csv()
df["Probability"] = pd.to_numeric(df["Probability"], errors="coerce").fillna(50).astype(int)
if "Prompt Time" not in df.columns:
    df["Prompt Time"] = ""

today_str = date.today().isoformat()
if "daily_responses" not in st.session_state or st.session_state.get("last_checked") != today_str:
    st.session_state.daily_responses = {}
    st.session_state.last_checked = today_str

if "updated_df" not in st.session_state:
    st.session_state.updated_df = df.copy()

# Ensure "Prompt Time" column exists in updated_df (in case session data lost it)
if "Prompt Time" not in st.session_state.updated_df.columns:
    st.session_state.updated_df["Prompt Time"] = df["Prompt Time"]

# --- Toggle for Editable Behavior Table ---
show_table = st.toggle("📝 Edit Behavior Table", value=False)
if show_table:
    edited_df = st.data_editor(st.session_state.updated_df, num_rows="dynamic", use_container_width=True)
else:
    edited_df = st.session_state.updated_df

# --- Daily Behavior Check-In ---
st.markdown("---")
st.header("Daily Behavior Check-In")

daily_df = edited_df[edited_df["Category"].str.lower() != "situational"]
st.write("🧪 Loaded daily behaviors:", len(daily_df))

for i, row in daily_df.iterrows():
    behavior = row["Behavior"]
    percent = row["Probability"]

    scheduled_time_str = row.get("Prompt Time", "00:00")
    if not scheduled_time_str or not isinstance(scheduled_time_str, str) or scheduled_time_str.strip() == "":
        continue
    try:
        scheduled_time = datetime.strptime(scheduled_time_str.strip(), "%H:%M").time()
    except ValueError:
        continue

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

if daily_df.empty:
    st.markdown("_⚠️ No daily behaviors to display. Check your CSV or Prompt Times._")

st.markdown("---")
with st.expander("🟣 Situational Logging"):
    situational_df = edited_df[edited_df["Category"].str.lower() == "situational"]
    for i, row in situational_df.iterrows():
        behavior = row["Behavior"]
        percent = row["Probability"]
        st.markdown(f"**{behavior}** — {percent}%")
        col1, col2 = st.columns(2)
        if col1.button(f"⬆️ Level Up '{behavior}'", key=f"situational_yes_{i}"):
            st.session_state.updated_df.at[i, "Probability"] = min(99, max(1, percent + 1))
            st.session_state.updated_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)
            st.rerun()
        if col2.button(f"⬇️ Level Down '{behavior}'", key=f"situational_no_{i}"):
            st.session_state.updated_df.at[i, "Probability"] = min(99, max(1, percent - 1))
            st.session_state.updated_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)
            st.rerun()