import streamlit as st
import pandas as pd
import numpy as np
import datetime
import threading

st.set_page_config(page_title="Behavior Tracker", page_icon="🧠", layout="centered")

st.markdown("""
    <style>
    .emoji-button {
        font-size: 2.5rem;
        width: 70px;
        height: 70px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 6px auto;
        border: 2px solid transparent;
        transition: all 0.2s ease-in-out;
    }
    .emoji-button:hover {
        box-shadow: 0 0 10px rgba(0,0,0,0.3);
        transform: scale(1.08);
    }
    .emoji-plus:hover {
        border-color: green;
        box-shadow: 0 0 12px green;
    }
    .emoji-minus:hover {
        border-color: red;
        box-shadow: 0 0 12px red;
    }
    .percentage-change {
        font-weight: bold;
        font-size: 1.1rem;
        margin-top: 5px;
        transition: opacity 0.5s ease-in-out;
        animation: fadeout 0.5s ease-in-out 6.5s forwards;
    }

    @keyframes fadeout {
        to {
            opacity: 0;
        }
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
    import time
    time.sleep(7)
    st.session_state.pop("percent_change_message", None)
    st.session_state.pop("percent_change_color", None)

remaining_behaviors = st.session_state.updated_df[~st.session_state.updated_df["Completed"]]

if not remaining_behaviors.empty:
    behavior_row = remaining_behaviors.iloc[0]
    behavior = behavior_row["Behavior"]
    percent = int(behavior_row["Probability"])
    index = behavior_row.name

    st.markdown(f"<div style='text-align:center;'><h2>{behavior}</h2><p style='font-size:0.9rem; color:#888;'>{percent}% chance</p></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(emoji_down_map.get(behavior, "❌"), key="no_btn", help="Didn't do", use_container_width=True):
            new_val = max(1, percent - 1)
            st.session_state.updated_df.at[index, "Probability"] = new_val
            st.session_state.updated_df.at[index, "Completed"] = True
            st.session_state.percent_change_message = f"{behavior} chance {percent}% → {new_val}%"
            st.session_state.percent_change_color = "red"
            threading.Thread(target=clear_percent_change).start()
            st.rerun()
    with col2:
        if st.button(emoji_up_map.get(behavior, "✅"), key="yes_btn", help="Did it", use_container_width=True):
            new_val = min(99, percent + 1)
            st.session_state.updated_df.at[index, "Probability"] = new_val
            st.session_state.updated_df.at[index, "Completed"] = True
            st.session_state.percent_change_message = f"{behavior} chance {percent}% → {new_val}%"
            st.session_state.percent_change_color = "green"
            threading.Thread(target=clear_percent_change).start()
            st.rerun()
else:
    st.success("✅ All check-ins completed or not yet scheduled.")

# Situational Behavior Tracker
if "Type" not in st.session_state.updated_df.columns:
    st.session_state.updated_df["Type"] = ""

with st.expander("📈 Situational Behaviors"):
    situational_df = st.session_state.updated_df[st.session_state.updated_df["Type"] == "Situational"].copy()
    for i, row in situational_df.iterrows():
        behavior = row["Behavior"]
        percent = int(row["Probability"])
        up_emoji = emoji_up_map.get(behavior, "✅")
        down_emoji = emoji_down_map.get(behavior, "❌")

        st.markdown(f"<h4 style='margin-bottom:2px;'>{behavior}</h4><p style='color:#888; margin-top:0;'>{percent}% chance</p>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([5, 1, 1, 5])
        with col2:
            if st.button(down_emoji, key=f"situational_down_{i}", help="Lower chance", use_container_width=True):
                new_val = max(1, percent - 1)
                st.session_state.updated_df.at[i, "Probability"] = new_val
                st.toast(f"{behavior} chance {percent}% → {new_val}%", icon="🔻")
                st.rerun()
        with col3:
            if st.button(up_emoji, key=f"situational_up_{i}", help="Increase chance", use_container_width=True):
                new_val = min(99, percent + 1)
                st.session_state.updated_df.at[i, "Probability"] = new_val
                st.toast(f"{behavior} chance {percent}% → {new_val}%", icon="🟢")
                st.rerun()

# Reset Button
if st.button("🔄 Reset Today's Check-ins"):
    st.session_state.updated_df["Completed"] = False
    st.rerun()

# Save
st.session_state.updated_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)