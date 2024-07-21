# Import python packages
import streamlit as st
import requests
import pandas as pd
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

cnx = st.connection("snowflake")
sessoin = cnx.session()

# Write directly to the app
st.title("Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie
    """
)

name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your Smoothie will be:", name_on_order)

session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).to_pandas()
#st.dataframe(data=my_dataframe, use_container_width=True)
pd_df=my_dataframe.copy()
st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingrediants:'
    , pd_df['FRUIT_NAME']
    , max_selections=5
    )
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        
        st.subheader(fruit_chosen + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/"+fruit_chosen)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, NAME_ON_ORDER)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""


   #st.write(my_insert_stmt)
   # st.stop()
    
    time_to_start = st.button('Submit Order')

    if time_to_start:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered'+', '+ name_on_order+'!', icon="✅")
