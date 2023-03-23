import streamlit as st
import base64
import folium


def hide_elements():
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        div[data-testid="stHeader"] {visibility: hidden;}
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
