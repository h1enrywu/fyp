import streamlit as st
from functions import hide_elements, set_bg_image


from pathlib import Path
from streamlit.source_util import (
    page_icon_and_name, 
    calc_md5, 
    get_pages,
    _on_pages_changed
)

def delete_page(main_script_path_str, page_name):

    current_pages = get_pages(main_script_path_str)
    st.write(current_pages)

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
    # st.write(list(pages_dir.glob("*.py"))+list(main_script_path.parent.glob("*.py")))
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


if st.button("delete"):
    delete_page("Introduction", "My_Dateset")

if st.button("add"):
     add_page("Introduction", "My_Dateset")



# 1. clear the cache
st.session_state.current_country = "None"

# 2. page config
# st.set_page_config(page_title="introduction-fpy", layout="centered")

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
        <h2>Interactive Visualization of Author Sentiments in Mask-related News</h2>
        <h2>Wu Ka Shing 21217424</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

# 5. background image
set_bg_image("mask_bg.jpg")
