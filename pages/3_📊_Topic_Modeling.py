import streamlit as st
from functions import hide_elements, logout_button
import streamlit.components.v1 as components
from PIL import Image


# 1. clear the cache
st.session_state.current_country = "None"

# 2. page config and logout button
st.set_page_config(
    page_title="topic-modeling-fpy",
    layout="wide",
)
logout_button()

# 3. import the css file
with open("style.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)


# 4. hide elements
hide_elements()

# 5. title
st.markdown(
    """
    <h2>Topic Modeling</h2><br>

    <style>
    iframe {
        
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 6. topic modeling
HtmlFile = open("lda.html", "r", encoding="utf-8")
source_code = HtmlFile.read()

with st.expander("🧩 Intertopic Distance Map"):
    components.html(source_code, height=800, width=1400, scrolling=True)

# 7. word clouds
word_cloud = Image.open("word_cloud.png")
topic1 = Image.open("topic1.png")
topic2 = Image.open("topic2.png")
topic3 = Image.open("topic3.png")
topic4 = Image.open("topic4.png")
topic5 = Image.open("topic5.png")
topic6 = Image.open("topic6.png")
topic7 = Image.open("topic7.png")
topic8 = Image.open("topic8.png")
topic9 = Image.open("topic9.png")
topic10 = Image.open("topic10.png")
topic11 = Image.open("topic11.png")
topic12 = Image.open("topic12.png")
topic13 = Image.open("topic13.png")
topic14 = Image.open("topic14.png")
topic15 = Image.open("topic15.png")
topic16 = Image.open("topic16.png")
topic17 = Image.open("topic17.png")
topic18 = Image.open("topic18.png")

(
    tab1,
    tab2,
    tab3,
    tab4,
    tab5,
    tab6,
    tab7,
    tab8,
    tab9,
    tab10,
    tab11,
    tab12,
    tab13,
    tab14,
    tab15,
    tab16,
    tab17,
    tab18,
    tab19,
) = st.tabs(
    [
        "All Topics",
        "Topic 1",
        "Topic 2",
        "Topic 3",
        "Topic 4",
        "Topic 5",
        "Topic 6",
        "Topic 7",
        "Topic 8",
        "Topic 9",
        "Topic 10",
        "Topic 11",
        "Topic 12",
        "Topic 13",
        "Topic 14",
        "Topic 15",
        "Topic 16",
        "Topic 17",
        "Topic 18",
    ]
)

with tab1:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(word_cloud, width=700)

with tab2:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic1, width=700)

with tab3:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic2, width=700)

with tab4:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic3, width=700)

with tab5:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic4, width=700)

with tab6:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic5, width=700)

with tab7:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic6, width=700)

with tab8:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic7, width=700)

with tab9:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic8, width=700)

with tab10:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic9, width=700)

with tab11:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic10, width=700)

with tab12:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic11, width=700)

with tab13:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic12, width=700)

with tab14:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic13, width=700)

with tab15:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic14, width=700)

with tab16:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic15, width=700)

with tab17:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic16, width=700)

with tab18:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic17, width=700)

with tab19:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col2.image(topic18, width=700)
