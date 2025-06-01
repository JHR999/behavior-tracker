import pandas as pd
import streamlit as st

# --- Dynamic Table for Editing Behaviors ---
@st.cache_data
def load_csv():
    return pd.read_csv("Behavior Tracking - Sheet1.csv")

df = load_csv()

edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# --- Daily Behavior Check-In ---
st.markdown("---")
st.header("Daily Behavior Check-In")

for i, row in edited_df.iterrows():
    behavior = row["Behavior"]
    percent = row["Probability"]

    st.markdown(f"**{behavior}** — {percent}%")
    col1, col2 = st.columns(2)
    if col1.button(f"✅ Did '{behavior}'", key=f"yes_{i}"):
        edited_df.at[i, "Probability"] = min(99, max(1, percent + 1))
        edited_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)
        st.rerun()
    if col2.button(f"❌ Didn't Do '{behavior}'", key=f"no_{i}"):
        edited_df.at[i, "Probability"] = min(99, max(1, percent - 1))
        edited_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)
        st.rerun()