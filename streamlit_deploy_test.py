import datetime
import json
import os
import urllib.request

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from streamlit_extras.let_it_rain import rain

import streamlit as st

# load the forecast data from the postgresql database
load_dotenv()

DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOSTNAME = os.environ["DB_HOSTNAME"]
DB_NAME = os.environ["DB_NAME"]

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:5432/{DB_NAME}")

df = pd.read_sql_query(
    """
    select * from customer_analytics.weather_forecast
    """,
    con=engine,
)
df["date"] = pd.to_datetime(df["date"])


def model_loader(date, rain_amount):
    if rain_amount:
        data = {"date": date, "rain_amount": rain_amount}
    else:
        data = {"date": date}
    body = str.encode(json.dumps(data))

    url = "https://modeleindpresentatie-endpoint.westeurope.inference.ml.azure.com/score"
    # Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
    api_key = "auCzBP0V4vDZMJncQlMjFe9dmJoxw812"
    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")

    # The azureml-model-deployment header will force the request to go to a specific deployment.
    # Remove this header to have the request observe the endpoint traffic rules
    headers = {
        "Content-Type": "application/json",
        "Authorization": ("Bearer " + api_key),
        "azureml-model-deployment": "modeleindpresentatie-deployment1",
    }

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        print(result)
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(error.read().decode("utf8", "ignore"))
    return result


def cool_effect():
    rain(
        emoji="💧",
        font_size=3 * rain_amount,
        falling_speed=1,
        animation_length=2,
    )


st.title("Deliverable Voorspelmodel Rotterdam")

# Allows you to pick a date in 2024
min_value = datetime.date.today()
max_value = datetime.date(2024, 12, 31)

date = st.date_input(
    "Voor welke datum wil je een voorspelling maken?", datetime.date.today(), min_value, max_value
)

if date in df["date"].dt.date.values:
    st.success("Er is een Weeronline neerslagvoorspelling beschikbaar voor deze datum")
    use_forecast = st.selectbox(
        "Hoe wil je de neerslag gebruiken?",
        [
            "Geen neerslag gebruiken",
            "Weeronline neerslagvoorspelling gebruiken",
            "Zelf voorspelling invoegen",
        ],
    )
    if use_forecast == "Weeronline neerslagvoorspelling gebruiken":
        rain_amount = float(df.loc[df["date"] == str(date), "precipitation forecast"].values)
        st.write(f"{rain_amount} mm")
        cool_effect()
    elif use_forecast == "Zelf voorspelling invoegen":
        rain_amount = st.text_input("Hoeveel mm regen verwacht je op deze dag?")
        if rain_amount:
            try:  # try if it is possible to convert the rain amount to integer
                st.write(f"{rain_amount} mm")  # print the number as a string
                rain_amount = float(rain_amount)
                cool_effect()
            except ValueError:
                st.error("Voer een getal in")
    elif use_forecast == "Geen neerslag gebruiken":
        rain_amount = None
else:
    st.info("Geen neerslagvoorspelling beschikbaar voor deze datum")
    custom_predict = st.selectbox("Wil je zelf neerslag toevoegen?", ["Nee", "Ja"])
    if custom_predict == "Ja":
        rain_amount = st.text_input("Hoeveel mm voorspel je op deze dag?")
        if rain_amount:
            try:  # try if it is possible to convert the rain amount to integer
                st.write(f"{rain_amount} mm")  # print the number as a string
                rain_amount = float(rain_amount)
                cool_effect()
            except ValueError:
                st.error("Voer een getal in")
    if custom_predict == "Nee":
        rain_amount = None


model_deploy = st.button("Maak voorspelling", type="primary")

date = str(date)
if model_deploy:
    with st.spinner("Model laden..."):
        try:
            result = model_loader(date, rain_amount)
            result = float(result)
            lower_bound_result = 0.92 * result
            upper_bound_result = 1.08 * result
            st.subheader(
                f"Het verwacht aantal bestellingen op deze dag is {int(result)}, Waarbij de verwachte hoeveelheid tussen {int(lower_bound_result)} en {int(upper_bound_result)} ligt."
            )
        except Exception:
            st.error("De voorspelling is te ver vooruit. Probeer een andere datum.")
