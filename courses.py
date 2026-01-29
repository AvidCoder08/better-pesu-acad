import streamlit as st
st.title("Courses")

def options_choice(sub,unit,mat):
    #write code here
    st.pdf(f"files/{sub}/{unit}/{mat}.pdf")
    
option1 = st.selectbox(label="Select Subject/Course",
             options=("Programming in C","Engineering Chemistry","Engineering Mechanic-Statics","Electronic Principles and Devices","Engineering Math 2","Constitution of India, Cyber Law and Personal Ethics"),
             index=None,)
option2 = st.selectbox(label="Select Unit",
                       options=("Unit 1","Unit 2","Unit 3","Unit 4"),
                       index=None)
option3 = st.selectbox(label="Choose material to view",
                       options=("Slides","Notes","QB","QA","Assignment","MCQs"),
                       index=None)
if option1 == None or option2 == None or option3 == None:
    st.warning("Select required criteria before viewing your materials")


if st.button("View Material"):
    options_choice(option1,option2,option3)
