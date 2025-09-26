import streamlit as st
import pandas as pd
import os
import plotly.express as px

#definir working directory
wd = os.path.dirname(os.path.abspath(__file__))

#charger les données
fem_path = os.path.join(wd, "..", "data", "processed", "feminicide_2022_2025.csv")
df_fem = pd.read_csv(fem_path)

#Etude par années
st.title("📊 Répartition annuelle des féminicides")

df_fem["année"] = pd.to_datetime(df_fem["date"], errors="coerce").dt.year
nb_fem = df_fem["année"].value_counts().sort_index()

fig_annee = px.bar(
    x=nb_fem.index,
    y=nb_fem.values,
    labels={"x": "Année", "y": "Nombre de féminicides"}
)

st.plotly_chart(fig_annee)

st.write("Le nombre de féminicides est malheureusement constant au cours du temps. La baisse observée en 2025 vient seulment du fait que les données s'arrêtent en août 2025. " \
"Il y a fort à parier que le nombre total de féminicides en 2025 sera similaire aux années précédentes.")