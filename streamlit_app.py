import streamlit as st
from snowflake.snowpark.functions import col

st.title("🥤 Customize Your Smoothie 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for customer name
name_on_order = st.text_input("Name on Smoothie: ")
st.write("The name on your smoothie will be:", name_on_order)

# Use Streamlit connection (reads from secrets.toml)
cnx = st.connection("snowflake")   # lowercase here matches secrets.toml
session = cnx.session()

# Query fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5,
)

if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    # SQL insert statement
    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
#st.text(smoothiefroot_response.json())
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
