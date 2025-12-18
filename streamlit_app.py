import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

st.title("🥤 Customize Your Smoothie 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for customer name
name_on_order = st.text_input("Name on Smoothie: ")
st.write("The name on your smoothie will be:", name_on_order)

# Use Streamlit connection (reads from .streamlit/secrets.toml)
cnx = st.connection("snowflake")   # lowercase matches secrets.toml
session = cnx.session()

# Query fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5,
)

if ingredients_list:
    # Build ingredients string
    ingredients_string = " ".join(ingredients_list)

    # Example SmoothieFroot API call (hardcoded watermelon for now)
    smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
    if smoothiefroot_response.ok:
        data = smoothiefroot_response.json()

        # Flatten the nutrition dictionary into separate columns
        nutrition_df = pd.json_normalize(data["nutrition"])

        st.subheader(f"Nutrition info for {data['name']}")
        st.dataframe(nutrition_df, use_container_width=True)

    # SQL insert statement
    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
