import streamlit as st
import pandas as pd
import os
import plotly.express as px


#definir working directory
wd = os.path.dirname(os.path.abspath(__file__))

#charger les données
fem_path = os.path.join(wd, "..", "data", "processed", "feminicide_2022_2025.csv")
df_fem = pd.read_csv(fem_path)

st.title("💔 Quel est le lien entre la victime et son meurtrier.e ?")


#Pichart à partir de la colonne 'meurtrier_cat'
tab_count = df_fem['meurtrier_cat'].value_counts()

fig_pie = px.pie(
    values=tab_count.values,
    names=tab_count.index,
    width=800,
    height=500
)

st.plotly_chart(fig_pie)

st.markdown("""Non, les femmes ne sont pas tuées par des inconnus mais surtout par **des gens de leur entourage proche** et notamment
            leur **conjoint** dans plus de 70% des cas. 
            """)






