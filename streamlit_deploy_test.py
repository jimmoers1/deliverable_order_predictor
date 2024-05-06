import datetime

import streamlit as st

st.title("Deliverable order predictor")

# Allows you to pick a date in 2024
min_value = datetime.date(2024, 1, 1)
max_value = datetime.date(2024, 12, 31)
date = st.date_input("What date would you like to predict?", datetime.date(2024, 1, 1), min_value, max_value)
st.write("You picked", str(date))

rain = st.selectbox("Is it going to rain on this day?", ["No", "Yes", "I don't know"])

# Creates an extra option that allows you to provide the amount of rain
if rain == "Yes":
    rain_amount = st.text_input("How much mm is it going to rain on this day?")
    if rain_amount:
        try:  # try if it is possible to convert the rain amount to integer
            int(rain_amount)
            st.write(rain_amount, "mm")  # print the number as a string
            rain_amount = int(rain_amount)  # change the number to an int
        except ValueError:
            st.error("Please provide a whole number")
    else:
        st.write("")  # doesn't display anything when no number is given
