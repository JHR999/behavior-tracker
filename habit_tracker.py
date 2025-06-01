import pandas as pd
import streamlit as st
from datetime import datetime, date, time

# --- Dynamic Table for Editing Behaviors ---
def load_csv():
    return pd.read_csv("Behavior Tracking - Sheet1.csv")

df = load_csv()
# Clean up column names (strip whitespace)
df.columns = df.columns.str.strip()
# Build emoji maps with safe fallbacks if columns are missing
emoji_up_map = dict(zip(df["Behavior"], df.get("+ Emoji", pd.Series(["✅"] * len(df)))))
emoji_down_map = dict(zip(df["Behavior"], df.get("- Emoji", pd.Series(["❌"] * len(df)))))
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

# --- Daily Behavior Check-In ---
st.markdown("---")

daily_df = st.session_state.updated_df[st.session_state.updated_df["Category"].str.lower() != "situational"]

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

# Add style block here before columns
st.markdown(
    """
    <style>
    .stButton > button {
        height: 120px;
        width: 120px;
        font-size: 80px;
        border-radius: 12px;
        text-align: center;
        padding: 0;
        line-height: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .stButton > button:hover {
        transform: scale(1.08);
    }
    .stButton > button:has-text("✅"), .stButton > button:has-text("🧠") {
        box-shadow: 0 0 12px rgba(0, 255, 0, 0.4);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# If there are habits to show
if not ready_df.empty:
    current_index = ready_df.index[st.session_state.daily_index % len(ready_df)]
    row = ready_df.loc[current_index]
    behavior = row["Behavior"]
    percent = row["Probability"]

    st.markdown(f"""
        <div style='border: 1px solid #444; border-radius: 12px; padding: 40px 30px 20px 30px; margin: 20px auto; text-align: center; max-width: 600px; background-color: #1e1e1e;'>
            <h2 style='font-size: 36px; color: white; margin-bottom: 30px;'>{behavior} — {percent}% Chance</h2>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(emoji_down_map.get(behavior, "❌"), key=f"down_btn_{current_index}", help="Didn't do it today"):
            st.session_state.updated_df.at[current_index, "Probability"] = min(99, max(1, percent - 1))
            st.session_state.updated_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)
            st.session_state.daily_responses[behavior] = True
            st.session_state.daily_index += 1
            st.rerun()
    with col2:
        if st.button(emoji_up_map.get(behavior, "✅"), key=f"up_btn_{current_index}", help="Did it today"):
            st.session_state.updated_df.at[current_index, "Probability"] = min(99, max(1, percent + 1))
            st.session_state.updated_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)
            st.session_state.daily_responses[behavior] = True
            st.session_state.daily_index += 1
            st.rerun()
else:
    st.markdown("_✅ All check-ins completed or not yet scheduled._")

if daily_df.empty:
    st.markdown("_⚠️ No daily behaviors to display. Check your CSV or Prompt Times._")

st.markdown("---")

with st.container():
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    with st.expander("🟣  **Situational Behaviors**  ", expanded=False):
        situational_df = st.session_state.updated_df[st.session_state.updated_df["Category"].astype(str).str.strip().str.lower() == "situational"]
        if situational_df.empty:
            st.markdown("_⚠️ No situational behaviors found._")
        for i in situational_df.index:
            row = situational_df.loc[i]
            behavior = row["Behavior"]
            percent = row["Probability"]
            st.markdown(f"**{behavior}** — {percent}% Chance")
            col1, col2 = st.columns(2)
            if col1.button(f"⬆️ Level Up '{behavior}'", key=f"situational_yes_{i}"):
                st.session_state.updated_df.at[i, "Probability"] = min(99, max(1, percent + 1))
                st.session_state.updated_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)
                st.rerun()
            if col2.button(f"⬇️ Level Down '{behavior}'", key=f"situational_no_{i}"):
                st.session_state.updated_df.at[i, "Probability"] = min(99, max(1, percent - 1))
                st.session_state.updated_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- Toggle for Editable Behavior Table ---
show_table = st.toggle("📝 Edit Behavior Table", value=False)
if show_table:
    edited_df = st.data_editor(st.session_state.updated_df, num_rows="dynamic", use_container_width=True)
else:
    edited_df = st.session_state.updated_df