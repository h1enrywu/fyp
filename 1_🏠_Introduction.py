import streamlit as st
from functions import hide_elements, set_bg_image


# 1. clear the cache
st.session_state.current_country = "None"

# 2. page config
st.set_page_config(page_title="introduction-fpy", layout="centered")

# 2. import the css file
with open("style.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

# 3. hide elements
hide_elements()

# 4. title
st.markdown(
    """
    <div class="intro_header">
        <h2>2022-23</h2>
        <h2>DMC Final Year Project</h2>
        <h2>Interactive Visualization of Author Sentiments in Health-related News</h2>
        <h2>Wu Ka Shing 21217424</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

# 5. background image
set_bg_image("mask_bg.jpg")
