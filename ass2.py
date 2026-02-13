import streamlit as st 
import datetime as dt

st.title("Age Calculator App")

name = st.text_input("Enter Your Name:")
n = dt.date(1947)
if len(name) != 0:
    st.write(f"Welcome to {name}! on App.")

    today = st.date_input("Enter Today date:", format="DD/MM/YYYY", value= None)
    dob = st.date_input("Enter Your Date of Birth:", format="DD/MM/YYYY", value= None, min_value=50,max_value=today)

    if today and dob is not None:
        age = (today - dob).days
        year = age // 365
        month = (age % 365) // 30
        day = ((age % 365) % 30)

        st.subheader(f"You are {year}year, {month}month, {day}day old!")
        st.success("Age Calculated, Sucessfully!")
