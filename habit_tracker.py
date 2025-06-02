import streamlit as st
import pandas as pd
import numpy as np
import datetime
import threading

st.set_page_config(page_title="Behavior Tracker", page_icon="🧠", layout="centered")

st.markdown("""
    <style>
    .emoji-button {
        font-size: 4.5rem;
        width: 90px;
        height: 90px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 6px auto;
        border: 2px solid transparent;
        transition: all 0.2s ease-in-out;
        cursor: pointer;
        user-select: none;
        background-color: transparent;
    }
    .emoji-button:hover {
        box-shadow: 0 0 15px rgba(0,0,0,0.5);
        transform: scale(1.12);
    }
    .emoji-plus {
        border-color: transparent;
    }
    .emoji-plus:hover {
        border-color: green;
        box-shadow: 0 0 18px limegreen;
    }
    .emoji-minus {
        border-color: transparent;
    }
    .emoji-minus:hover {
        border-color: red;
        box-shadow: 0 0 18px red;
    }
    .percentage-change {
        font-weight: bold;
        font-size: 1.1rem;
        margin-top: 5px;
        transition: opacity 0.5s ease-in-out;
        /* Removed animation to keep message visible */
        text-align: center;
    }
    .button-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .situational-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    .situational-behavior {
        flex: 5;
        font-weight: 600;
        font-size: 1.1rem;
    }
    .situational-percent {
        flex: 1;
        color: #888;
        text-align: center;
        font-size: 0.95rem;
    }
    .situational-buttons {
        flex: 2;
        display: flex;
        justify-content: center;
        gap: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_df():
    return pd.read_csv("Behavior Tracking - Sheet1.csv")

df = load_df()
if "updated_df" not in st.session_state:
    st.session_state.updated_df = df.copy()
if "Completed" not in st.session_state.updated_df.columns:
    st.session_state.updated_df["Completed"] = False
if "Type" not in st.session_state.updated_df.columns:
    st.session_state.updated_df["Type"] = ""

# Emoji Mappings
emoji_up_map = dict(zip(df["Behavior"], df.get("+ Emoji", pd.Series(["✅"] * len(df))).fillna("✅")))
emoji_down_map = dict(zip(df["Behavior"], df.get("- Emoji", pd.Series(["❌"] * len(df))).fillna("❌")))

# Behavior Check-In
st.title("Behavior Check-In")

if "percent_change_message" in st.session_state:
    st.markdown(
        f"<p class='percentage-change' style='color:{st.session_state['percent_change_color']};'>{st.session_state['percent_change_message']}</p>",
        unsafe_allow_html=True
    )

def clear_percent_change():
    def clear_and_rerun():
        st.session_state.pop("percent_change_message", None)
        st.session_state.pop("percent_change_color", None)
        st.experimental_rerun()
    # Use threading.Timer to delay clearing
    timer = threading.Timer(7.0, clear_and_rerun)
    timer.start()

remaining_behaviors = st.session_state.updated_df[~st.session_state.updated_df["Completed"]]

if not remaining_behaviors.empty:
    behavior_row = remaining_behaviors.iloc[0]
    behavior = behavior_row["Behavior"]
    percent = int(behavior_row["Probability"])
    index = behavior_row.name

    st.markdown(f"<div style='text-align:center;'><h2>{behavior}</h2><p style='font-size:0.9rem; color:#888;'>{percent}% chance</p></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="small")
    with col1:
        # Use button with emoji inside so hover effects apply properly
        if st.button(f"{emoji_down_map.get(behavior, '❌')}", key="no_btn", help="Didn't do", use_container_width=True):
            new_val = max(1, percent - 1)
            st.session_state.updated_df.at[index, "Probability"] = new_val
            st.session_state.updated_df.at[index, "Completed"] = True
            st.session_state.percent_change_message = f"{behavior} chance {percent}% → {new_val}%"
            st.session_state.percent_change_color = "red"
            clear_percent_change()
    with col2:
        if st.button(f"{emoji_up_map.get(behavior, '✅')}", key="yes_btn", help="Did it", use_container_width=True):
            new_val = min(99, percent + 1)
            st.session_state.updated_df.at[index, "Probability"] = new_val
            st.session_state.updated_df.at[index, "Completed"] = True
            st.session_state.percent_change_message = f"{behavior} chance {percent}% → {new_val}%"
            st.session_state.percent_change_color = "green"
            clear_percent_change()

    # Apply CSS classes to buttons via st.markdown hack to get hover effects and size
    st.markdown(
        f"""
        <style>
        div.stButton > button:first-child {{
            font-size: 4.5rem !important;
            border-radius: 12px !important;
            border: 2px solid transparent !important;
            cursor: pointer !important;
            user-select: none !important;
            background-color: transparent !important;
            transition: all 0.2s ease-in-out !important;
            width: 90px !important;
            height: 90px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 auto !important;
        }}
        div.stButton > button:first-child:hover {{
            box-shadow: 0 0 15px rgba(0,0,0,0.5) !important;
            transform: scale(1.12) !important;
        }}
        div.stButton > button:first-child[aria-label="Did it"]:hover {{
            border-color: green !important;
            box-shadow: 0 0 18px limegreen !important;
        }}
        div.stButton > button:first-child[aria-label="Didn't do"]:hover {{
            border-color: red !important;
            box-shadow: 0 0 18px red !important;
        }}
        </style>
        """, unsafe_allow_html=True
    )

else:
    st.success("✅ All check-ins completed or not yet scheduled.")

# Situational Behavior Tracker
with st.expander("📈 Situational Behaviors"):
    situational_df = st.session_state.updated_df[st.session_state.updated_df["Type"] == "Situational"].copy()
    for i, row in situational_df.iterrows():
        behavior = row["Behavior"]
        percent = int(row["Probability"])
        up_emoji = emoji_up_map.get(behavior, "✅")
        down_emoji = emoji_down_map.get(behavior, "❌")

        st.markdown(
            f"""
            <div class="situational-row">
                <div class="situational-behavior">{behavior}</div>
                <div class="situational-percent">{percent}% chance</div>
                <div class="situational-buttons">
                    <form action="#" method="POST" id="form_down_{i}">
                        <button type="submit" name="action" value="down_{i}" class="emoji-button emoji-minus" title="Lower chance" style="font-size: 3.5rem;">{down_emoji}</button>
                    </form>
                    <form action="#" method="POST" id="form_up_{i}">
                        <button type="submit" name="action" value="up_{i}" class="emoji-button emoji-plus" title="Increase chance" style="font-size: 3.5rem;">{up_emoji}</button>
                    </form>
                </div>
            </div>
            """, unsafe_allow_html=True
        )
        # Use st.button with unique keys for interactivity and consistent style
        col1, col2, col3 = st.columns([5, 1, 1], gap="small")
        with col2:
            if st.button("", key=f"situational_down_{i}", help="Lower chance", use_container_width=True):
                new_val = max(1, percent - 1)
                st.session_state.updated_df.at[i, "Probability"] = new_val
                st.session_state.percent_change_message = f"{behavior} chance {percent}% → {new_val}%"
                st.session_state.percent_change_color = "red"
                clear_percent_change()
        with col3:
            if st.button("", key=f"situational_up_{i}", help="Increase chance", use_container_width=True):
                new_val = min(99, percent + 1)
                st.session_state.updated_df.at[i, "Probability"] = new_val
                st.session_state.percent_change_message = f"{behavior} chance {percent}% → {new_val}%"
                st.session_state.percent_change_color = "green"
                clear_percent_change()

# Reset Button
if st.button("🔄 Reset Today's Check-ins"):
    st.session_state.updated_df["Completed"] = False

# Save
st.session_state.updated_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)