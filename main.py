import streamlit as st
st.set_page_config(page_title="Better PESU", page_icon=":books:", layout="wide")
logo_svg = """
<svg width="200" height="50">
  <text x="0" y="40" font-family="Segoe UI Variable Display" font-size="40" fill='#fafafa'>Hail Mary</text>
</svg>
"""
st.logo(logo_svg)

pg = st.navigation([
    st.Page("dashboard.py",title="Dashboard",icon=":material/dashboard:"),
    st.Page("courses.py", title="Courses",icon=":material/backpack:"),
    st.Page("marks.py", title="Grades",icon=":material/trophy:"),
    st.Page("settings.py",title="Settings",icon=":material/settings:")
])

pg.run()