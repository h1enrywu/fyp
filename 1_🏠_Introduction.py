import streamlit as st
from functions import hide_elements, set_bg_image, login_panel, delete_page, logout_button


# 1. clear the cache
st.session_state.current_country = "None"

# 2. page config
st.set_page_config(page_title="introduction-fpy", layout="centered")

# 3. import the css file
with open("style.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

# 4. Login & Logout
if "is_login" not in st.session_state:
    st.session_state.is_login = "No"

if st.session_state.is_login == "No":
    delete_page("Introduction", "My_Dateset")
    delete_page("Introduction", "Topic_Modeling")
    delete_page("Introduction", "Sentiment_Analysis")
    login_panel()

if st.session_state.is_login == "Yes":
    logout_button()

# 5. hide elements
hide_elements()

# 6. title
st.markdown(
    """
    <div class="intro_header">
        <h2>2022-23</h2>
        <h2>DMC Final Year Project</h2>
        <h2>Interactive Visualization of Author Sentiments in Mask-related News</h2>
        <h2>Wu Ka Shing 21217424</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

# 7. background image
set_bg_image("mask_bg.jpg")
