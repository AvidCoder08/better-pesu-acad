import streamlit as st
st.set_page_config(page_title="Better PESU", page_icon=":books:", layout="wide")
# st.markdown("""
# <style>
#     #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
# </style>
# """,unsafe_allow_html=True)

pg = st.navigation([
    st.Page("dashboard.py",title="Dashboard",icon=":material/dashboard:"),
    st.Page("courses.py", title="Courses",icon=":material/backpack:"),
    st.Page("marks.py", title="Grades",icon=":material/trophy:"),
    st.Page("settings.py",title="Settings",icon=":material/settings:")
],position="top")
pg.run()