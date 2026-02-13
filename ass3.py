import streamlit as st

st.title("Favroit Location Chhoser APP")

col1, col2 = st.columns(2)

with col1:
    st.header("Village")
    st.image("https://images.pexels.com/photos/4856510/pexels-photo-4856510.jpeg", width=400)
    vote1 = st.button("Vote for Village")

with col2:
    st.header("City")
    st.image("https://images.pexels.com/photos/13441982/pexels-photo-13441982.jpeg", width=400)
    vote2 = st.button("Vote for City")

if vote1:
    st.success("You choose Village. Great Choice! ")
    village = st.text_input("Enter Your Village Name:")

elif vote2:
    st.success("You choose City. Great Choice! ")
    city = st.text_input("Enter Your City Name:")
