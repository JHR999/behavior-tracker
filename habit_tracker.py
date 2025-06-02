import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="Behavior Tracker", page_icon="🧠", layout="centered")

st.markdown("""
    <style>
    .emoji-button {
        font-size: 2rem;
        width: 80px;
        height: 80px;
        border-radius: 15px;
        display: inline-block;
        text-align: center;
        line-height: 80px;
        margin: 10px;
        border: 2px solid transparent;
        transition: all 0.2s ease-in-out;
    }
    .emoji-button:hover {
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        background-color: #f0f0f0;
    }
    .emoji-plus:hover {
        border-color: green;
    }
    .emoji-minus:hover {
        border-color: red;
    }
    .percentage-change {
        font-weight: bold;
        font-size: 1.1rem;
        margin-top: 5px;
        transition: opacity 0.5s ease-in-out;
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

# Emoji Mappings
emoji_up_map = dict(zip(df["Behavior"], df.get("+ Emoji", pd.Series(["✅"] * len(df))).fillna("✅")))
emoji_down_map = dict(zip(df["Behavior"], df.get("- Emoji", pd.Series(["❌"] * len(df))).fillna("❌")))

# Behavior Check-In
st.title("Behavior Check-In")

remaining_behaviors = st.session_state.updated_df[~st.session_state.updated_df["Completed"]]

if not remaining_behaviors.empty:
    behavior_row = remaining_behaviors.iloc[0]
    behavior = behavior_row["Behavior"]
    percent = int(behavior_row["Probability"])
    index = behavior_row.name

    st.markdown(f"<h2 style='text-align:center;'>{behavior}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#aaa; margin-top:-10px'>{percent}% chance</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(emoji_down_map.get(behavior, "❌"), key="no_btn", help="Didn't do", use_container_width=True):
            new_val = max(1, percent - 1)
            st.session_state.updated_df.at[index, "Probability"] = new_val
            st.session_state.updated_df.at[index, "Completed"] = True
            st.toast(f"{behavior} chance {percent}% → {new_val}%", icon="🔻")
            st.experimental_rerun()
    with col2:
        if st.button(emoji_up_map.get(behavior, "✅"), key="yes_btn", help="Did it", use_container_width=True):
            new_val = min(99, percent + 1)
            st.session_state.updated_df.at[index, "Probability"] = new_val
            st.session_state.updated_df.at[index, "Completed"] = True
            st.toast(f"{behavior} chance {percent}% → {new_val}%", icon="🟢")
            st.experimental_rerun()
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

        st.markdown(f"<h4 style='margin-bottom:2px;'>{behavior}</h4><p style='color:#888; margin-top:0;'>{percent}% chance</p>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(down_emoji, key=f"situational_down_{i}", help="Lower chance", use_container_width=True):
                new_val = max(1, percent - 1)
                st.session_state.updated_df.at[i, "Probability"] = new_val
                st.toast(f"{behavior} chance {percent}% → {new_val}%", icon="🔻")
                st.experimental_rerun()
        with col2:
            if st.button(up_emoji, key=f"situational_up_{i}", help="Increase chance", use_container_width=True):
                new_val = min(99, percent + 1)
                st.session_state.updated_df.at[i, "Probability"] = new_val
                st.toast(f"{behavior} chance {percent}% → {new_val}%", icon="🟢")
                st.experimental_rerun()

# Reset Button
if st.button("🔄 Reset Today's Check-ins"):
    st.session_state.updated_df["Completed"] = False
    st.experimental_rerun()

# Save
st.session_state.updated_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)