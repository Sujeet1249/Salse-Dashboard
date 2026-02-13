import streamlit as st

st.title("Programing Language Peekr App")
st.subheader("Welcom to our App")

programing = st.selectbox("Choose your favriote Programing Language: ", ["C", "C++", "Python", "Javascript", "Java", "React"])
st.write(f"You choose {programing} langauge.")

st.success("Great! Your choice is best.")