import pandas as pd
import streamlit as st
from datetime import datetime, date, time
from streamlit.components.v1 import html

st.markdown("""
<style>
.situational-btn {
    font-size: 42px;
    padding: 12px 28px;
    border-radius: 14px;
    border: none;
    cursor: pointer;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.situational-btn:hover {
    transform: scale(1.05);
}
.situational-up {
    background-color: #2e8b57;
    color: white;
}
.situational-up:hover {
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.7);
}
.situational-down {
    background-color: #8b2e2e;
    color: white;
}
.situational-down:hover {
    box-shadow: 0 0 20px rgba(255, 0, 0, 0.7);
}
</style>
""", unsafe_allow_html=True)

# --- Dynamic Table for Editing Behaviors ---
def load_csv():
    return pd.read_csv("Behavior Tracking - Sheet1.csv")

def render_emoji_buttons(behavior, percent, index):
    up_emoji = emoji_up_map.get(behavior, "✅")
    down_emoji = emoji_down_map.get(behavior, "❌")
    st.markdown(f"""
    <style>
    .emoji-btn-container {{
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-top: 20px;
    }}
    .emoji-btn {{
        font-size: 70px;
        height: 100px;
        width: 100px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        background-color: #111;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: none;
        border: 3px solid #555;
    }}
    .emoji-btn:hover {{
        transform: translateY(-5px);
    }}
    .emoji-btn.up:hover {{
        transform: scale(1.1) translateY(-4px);
        box-shadow: 0 0 25px rgba(0,255,0,0.6), 0 0 50px rgba(0,255,0,0.4);
        border-color: limegreen;
    }}
    .emoji-btn.down:hover {{
        transform: scale(1.1) translateY(-4px);
        box-shadow: 0 0 25px rgba(255,0,0,0.6), 0 0 50px rgba(255,0,0,0.4);
        border-color: red;
    }}
    </style>

    <div class="emoji-btn-container">
        <a href="?action=down&index={index}" class="emoji-btn down">{down_emoji}</a>
        <a href="?action=up&index={index}" class="emoji-btn up">{up_emoji}</a>
    </div>
    """, unsafe_allow_html=True)

df = load_csv()
# Clean up column names (strip whitespace)
df.columns = df.columns.str.strip()
df["+ Emoji"] = df["+ Emoji"].fillna("✅")
df["- Emoji"] = df["- Emoji"].fillna("❌")
emoji_up_map = dict(zip(df["Behavior"], df["+ Emoji"]))
emoji_down_map = dict(zip(df["Behavior"], df["- Emoji"]))
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

if "last_change_msg" not in st.session_state:
    st.session_state["last_change_msg"] = ""

# --- Daily Behavior Check-In ---

# Display last change message if available (centered, font size 24px, custom color via HTML span)
if st.session_state["last_change_msg"]:
    st.markdown(f"<p style='text-align: center; font-size: 24px;'>{st.session_state['last_change_msg']}</p>", unsafe_allow_html=True)
    st.markdown("""
    <script>
      setTimeout(function() {
        var el = window.parent.document.querySelector('[data-testid="stMarkdownContainer"] > div');
        if (el) { el.style.display = 'none'; }
      }, 7000);
    </script>
    """, unsafe_allow_html=True)
    st.session_state["last_change_msg"] = ""

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
    height: 110px;
    width: 110px;
    font-size: 90px;
    border-radius: 16px;
    text-align: center;
    padding: 0;
    line-height: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    background-color: #111;
    border: 3px solid #444;
    margin: 0 10px;
    box-sizing: border-box;
    color: white;
}

.stButton button[data-testid="button-element"][id*="down_btn_"] {
    border-color: red !important;
}

.stButton button[data-testid="button-element"][id*="down_btn_"]:hover {
    transform: translateY(-6px);
    box-shadow: 0 0 25px rgba(255, 0, 0, 0.9), 0 0 40px rgba(255, 0, 0, 0.6);
}

.stButton button[data-testid="button-element"][id*="up_btn_"] {
    border-color: #00ff00 !important;
}

.stButton button[data-testid="button-element"][id*="up_btn_"]:hover {
    transform: translateY(-6px);
    box-shadow: 0 0 25px rgba(0, 255, 0, 0.9), 0 0 40px rgba(0, 255, 0, 0.6);
}
</style>
    """,
    unsafe_allow_html=True,
)

try:
    query_params = st.query_params
    if "action" in query_params and "index" in query_params:
        index = int(query_params["index"][0])
        action = query_params["action"][0]
        if 0 <= index < len(st.session_state.updated_df):
            behavior = st.session_state.updated_df.at[index, "Behavior"]
            percent = st.session_state.updated_df.at[index, "Probability"]
            if behavior not in st.session_state.daily_responses:
                if action == "up":
                    st.session_state.updated_df.at[index, "Probability"] = min(99, max(1, percent + 1))
                elif action == "down":
                    st.session_state.updated_df.at[index, "Probability"] = min(99, max(1, percent - 1))
                st.session_state.updated_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)
                st.session_state.daily_responses[behavior] = True
                st.session_state.daily_index += 1
                st.query_params.clear()
                st.rerun()
except Exception as e:
    st.warning(f"⚠️ Could not parse action or index from query parameters. Error: {e}")

import time

# --- Daily Behavior Card Rendering ---
if not ready_df.empty:
    current_index = ready_df.index[st.session_state.daily_index % len(ready_df)]
    row = ready_df.loc[current_index]
    behavior = row["Behavior"]
    percent = row["Probability"]

    st.markdown(f"""
        <div class="daily-checkin-card">
            <h2 style='font-size: 50px; color: white; margin-bottom: 10px;'>{behavior}</h2>
            <p style='font-size: 20px; color: #ccc; margin: 0;'>{percent}% Chance</p>
        </div>
    """, unsafe_allow_html=True)

    # Render emoji buttons horizontally centered below the card
    with st.container():
        st.markdown('<div class="emoji-buttons-container">', unsafe_allow_html=True)
        render_emoji_buttons(behavior, percent, current_index)
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="daily-checkin-card">
            <h2 style='font-size: 30px; color: white; margin-bottom: 10px;'>✅ All check-ins completed or not yet scheduled.</h2>
        </div>
    """, unsafe_allow_html=True)

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
            down_emoji = emoji_down_map.get(behavior, "❌")
            up_emoji = emoji_up_map.get(behavior, "✅")
            st.markdown(f"""
                <div style="margin-bottom: 20px; padding: 10px; border-radius: 10px; background-color: #1a1a1a;">
                    <div style="font-weight: bold; font-size: 18px; color: white; margin-bottom: 5px;">{behavior} — <span style="color: #ccc;">{percent}% Chance</span></div>
                    <div style="display: flex; justify-content: center; gap: 30px; margin-top: 10px;">
                        <a href="?situational_action=down&index={i}" class="emoji-btn down" style="font-size:70px;height:100px;width:100px;display:flex;align-items:center;justify-content:center;text-decoration:none;">{down_emoji}</a>
                        <a href="?situational_action=up&index={i}" class="emoji-btn up" style="font-size:70px;height:100px;width:100px;display:flex;align-items:center;justify-content:center;text-decoration:none;">{up_emoji}</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Situational button action handling (no page reload) ---
try:
    query_params = st.query_params
    if "situational_action" in query_params and "index" in query_params:
        index = int(query_params["index"][0])
        action = query_params["situational_action"][0]
        if 0 <= index < len(st.session_state.updated_df):
            percent = st.session_state.updated_df.at[index, "Probability"]
            if action == "up":
                st.session_state.updated_df.at[index, "Probability"] = min(99, max(1, percent + 1))
            elif action == "down":
                st.session_state.updated_df.at[index, "Probability"] = min(99, max(1, percent - 1))
            st.session_state.updated_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)
            st.query_params.clear()
            st.rerun()
except Exception as e:
    st.warning(f"⚠️ Could not parse situational action or index from query parameters. Error: {e}")

# --- Toggle for Editable Behavior Table ---
show_table = st.toggle("📝 Edit Behavior Table", value=False)
if show_table:
    edited_df = st.data_editor(st.session_state.updated_df, num_rows="dynamic", use_container_width=True)
else:
    edited_df = st.session_state.updated_df

# --- Reset Daily Check-In State ---
if st.button("🔄 Reset Today's Responses"):
    st.session_state.daily_responses = {}
    st.session_state.daily_index = 0
    st.rerun()