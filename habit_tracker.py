st.markdown(
    """
<style>
.stButton > button {
    height: 100px;
    width: 100px;
    font-size: 60px;
    border-radius: 12px;
    text-align: center;
    padding: 0;
    line-height: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #222;
    border: 2px solid #444;
    margin: 0 10px;
    transition: box-shadow 0.3s ease;
}

.stButton button[data-testid="button-element"][id*="down_btn_"]:hover {
    box-shadow: 0 0 15px 3px rgba(255, 0, 0, 0.6);
}

.stButton button[data-testid="button-element"][id*="up_btn_"]:hover {
    box-shadow: 0 0 15px 3px rgba(0, 255, 0, 0.6);
}
</style>
    """,
    unsafe_allow_html=True,
)