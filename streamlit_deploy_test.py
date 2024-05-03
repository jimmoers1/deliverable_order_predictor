import datetime

import streamlit as st

st.title("Deliverable order predictor")

# Allows you to pick a date in 2024
min_value = datetime.date(2024, 1, 1)
max_value = datetime.date(2024, 12, 31)
date = st.date_input("What date would you like to predict?", datetime.date(2024, 1, 1), min_value, max_value)
st.write("You picked", date)

rain = st.selectbox("is it going to rain on this day?", ["no", "yes"])

if rain == "yes":
    rain_amount = st.text_input("How much mm is it going to rain on this day?")
    if rain_amount:
        st.write(rain_amount, "mm")
    else:
        st.write("")
