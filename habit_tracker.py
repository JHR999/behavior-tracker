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

daily_df = edited_df[edited_df["Category"].str.lower() != "situational"]

# Filter behaviors ready to be answered
ready_df = daily_df.copy()
ready_df["Prompt Time"] = ready_df["Prompt Time"].astype(str).str.strip()
ready_df = ready_df[ready_df["Prompt Time"] != ""]
ready_df["Scheduled"] = pd.to_datetime(ready_df["Prompt Time"], format="%H:%M", errors="coerce").dt.time
now = datetime.now().time()

# Only show behaviors that are scheduled and unanswered
ready_df = ready_df[
    ready_df["Scheduled"].apply(lambda t: t is not pd.NaT and now >= t)
    & ~ready_df["Behavior"].isin(st.session_state.daily_responses)
]

# Sort to make experience consistent
ready_df = ready_df.sort_values("Prompt Time")

# Track progress index
if "daily_index" not in st.session_state:
    st.session_state.daily_index = 0

# If there are habits to show
if not ready_df.empty:
    current_index = ready_df.index[st.session_state.daily_index % len(ready_df)]
    row = ready_df.loc[current_index]
    behavior = row["Behavior"]
    percent = row["Probability"]

    st.markdown(f"""
        <div style='border: 1px solid #444; border-radius: 12px; padding: 40px 30px 20px 30px; margin: 20px auto; text-align: center; max-width: 600px; background-color: #1e1e1e;'>
            <h2 style='font-size: 36px; color: white; margin-bottom: 30px;'>{behavior} — {percent}%</h2>
            <div style='display: flex; justify-content: center; gap: 60px;'>
                <form action="?yes=true" method="post">
                    <button style="font-size: 32px; padding: 20px 40px; border-radius: 12px; background-color: #444; color: white; border: none;" name="response" value="yes">✅</button>
                </form>
                <form action="?no=true" method="post">
                    <button style="font-size: 32px; padding: 20px 40px; border-radius: 12px; background-color: #444; color: white; border: none;" name="response" value="no">❌</button>
                </form>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Button triggers
    if st.query_params.get("yes") == "true":
        st.session_state.updated_df.at[current_index, "Probability"] = min(99, max(1, percent + 1))
        st.session_state.updated_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)
        st.session_state.daily_responses[behavior] = True
        st.session_state.daily_index += 1
        st.experimental_set_query_params()  # Clear query params
        st.rerun()
    elif st.query_params.get("no") == "true":
        st.session_state.updated_df.at[current_index, "Probability"] = min(99, max(1, percent - 1))
        st.session_state.updated_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)
        st.session_state.daily_responses[behavior] = True
        st.session_state.daily_index += 1
        st.experimental_set_query_params()
        st.rerun()
else:
    st.markdown("_✅ All check-ins completed or not yet scheduled._")

if daily_df.empty:
    st.markdown("_⚠️ No daily behaviors to display. Check your CSV or Prompt Times._")

st.markdown("---")
with st.expander("🟣  **Situational Logging**  ", expanded=False):
    situational_df = edited_df[edited_df["Category"].astype(str).str.strip().str.lower() == "situational"]
    if situational_df.empty:
        st.markdown("_⚠️ No situational behaviors found._")
    for i in situational_df.index:
        row = situational_df.loc[i]
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