with st.form(key=f"situational_form_{i}", clear_on_submit=False):
    selected_action = st.radio("Choose Action", [down_emoji, up_emoji], horizontal=True, key=f"radio_{i}")
    submit = st.form_submit_button("Submit", key=f"situational_submit_{i}")

    if submit:
        current_prob = st.session_state.updated_df.at[i, "Probability"]
        if selected_action == down_emoji:
            st.session_state.updated_df.at[i, "Probability"] = min(99, max(1, current_prob - 1))
        else:
            st.session_state.updated_df.at[i, "Probability"] = min(99, max(1, current_prob + 1))
        st.session_state.updated_df.to_csv("Behavior Tracking - Sheet1.csv", index=False)
        st.experimental_rerun()