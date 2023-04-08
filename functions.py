import streamlit as st
import base64
import folium
from wordcloud import WordCloud
import numpy as np
from PIL import Image
from streamlit.runtime.scriptrunner import RerunData, RerunException
from pathlib import Path
from streamlit.source_util import (
    page_icon_and_name, 
    calc_md5, 
    get_pages,
    _on_pages_changed
)


def hide_elements():
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        div[data-testid="stHeader"] {visibility: hidden;}
        .viewerBadge_link__1S137 {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_map():
    map = folium.Map(
        location=[-3.03395, 22.94755],
        tiles="cartodbpositron",
        zoom_start=1,
        min_zoom=1,
        max_zoom=4,
    )
    country_coordinates = {
        "Australia": (-24.94685, 133.85727),
        "China": (35.13445, 102.69069),
        "Hong Kong": (22.32667, 114.17228),
        "Japan": (35.87259, 137.98691),
        "Singapore": (1.36685, 103.86003),
        "South Korea": (36.53381, 127.83560),
        "United Kingdom": (55.08164, -2.61579),
        "United States": (39.74855, -101.19145),
    }
    country_colors = {
        "Australia": "red",
        "China": "blue",
        "Hong Kong": "green",
        "Japan": "purple",
        "Singapore": "orange",
        "South Korea": "darkred",
        "United Kingdom": "lightred",
        "United States": "beige",
    }
    for country, coordinates in country_coordinates.items():
        folium.Marker(
            location=coordinates,
            popup=country,
            icon=folium.Icon(color=country_colors[country], icon="info-sign"),
        ).add_to(map)

    return map


@st.cache_data
def set_bg_image(image):
    with open(image, "rb") as image:
        encoded_string = base64.b64encode(image.read())
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
                background-size: cover
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def create_word_cloud(text, max_words):
    mask = np.array(Image.open("cloud.png"))

    stopwords = {"people", "year", "day", "week", "time", "month", "hong", "kong"}

    wordcloud = WordCloud(
        background_color="#fbfbfd",
        max_words=max_words,
        stopwords=stopwords,
        mask=mask,
    ).generate(text)

    return wordcloud


def delete_page(main_script_path_str, page_name):

    current_pages = get_pages(main_script_path_str)
    # st.write(current_pages)

    for key, value in current_pages.items():
        if value['page_name'] == page_name:
            del current_pages[key]
            break
        else:
            pass
    _on_pages_changed.send()


def add_page(main_script_path_str, page_name):
    
    pages = get_pages(main_script_path_str)
    main_script_path = Path(main_script_path_str)
    pages_dir = main_script_path.parent / "pages"
    script_path = [f for f in list(pages_dir.glob("*.py"))+list(main_script_path.parent.glob("*.py")) if f.name.find(page_name) != -1][0]
    script_path_str = str(script_path.resolve())
    pi, pn = page_icon_and_name(script_path)
    psh = calc_md5(script_path_str)
    pages[psh] = {
        "page_script_hash": psh,
        "page_name": pn,
        "icon": pi,
        "script_path": script_path_str,
    }
    _on_pages_changed.send()


def login_panel():
    empty = st.sidebar.empty()
    with empty.expander("Login Panel", expanded=True):
        ac = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if ac == "admin" and pw == "admin":
                add_page("Introduction", "My_Dateset")
                add_page("Introduction", "Topic_Modeling")
                add_page("Introduction", "Sentiment_Analysis")
                st.session_state.is_login = "Yes"
                empty.empty()
            else:
                st.error("Invalid username or password")


def logout_button():
    def switch_page(page_name: str):


        def standardize_name(name: str) -> str:
            return name.lower().replace("_", " ")

        page_name = standardize_name(page_name)

        pages = get_pages("streamlit_app.py")  # OR whatever your main page is called

        for page_hash, config in pages.items():
            if standardize_name(config["page_name"]) == page_name:
                raise RerunException(
                    RerunData(
                        page_script_hash=page_hash,
                        page_name=page_name,
                    )
                )

        page_names = [standardize_name(config["page_name"]) for config in pages.values()]

        raise ValueError(f"Could not find page {page_name}. Must be one of {page_names}")
    
    if st.sidebar.button("Logout"):
        st.session_state.is_login = "No"
        switch_page("Introduction")
            