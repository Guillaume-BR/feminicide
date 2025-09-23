import streamlit as st
import pandas as pd
import os
import folium
from streamlit_folium import st_folium
import geopandas as gpd

st.title("📊 Statistiques")

#ecrire en plus gros
st.markdown("<h2>Est ce que celà dépend des années ?</h2>", unsafe_allow_html=True)

#definir working directory
wd = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(wd, "..", "data", "processed", "feminicide_2022_2025.csv")
df_fem = pd.read_csv(data_path)

# Statistiques simples
df_fem["année"] = pd.to_datetime(df_fem["date"], errors="coerce").dt.year
stats = df_fem["année"].value_counts().sort_index()
st.bar_chart(stats)

st.write("Est ce que celà dépend de l'âge ?")
age_stats = df_fem["age"].value_counts().sort_index()
#regrouper par tranche de 5 ans
age_stats = age_stats.groupby(pd.cut(age_stats.index, range(0, 101, 5))).sum()
st.bar_chart(age_stats)

st.write("Et par zone géographique ?")

#charger les données des départements
json_dep = gpd.read_file(os.path.join(wd, "..", "data", "processed", "departements_feminicide.geojson"))

#charger les données des féminicides par département
df_total_dep = pd.read_csv(os.path.join(wd, "..", "data", "processed", "df_total_dep.csv"))

# Créer la carte
location = [47, 3.2]  # centre de la France
zoom = 6
Carte = folium.Map(location=location, zoom_start=zoom, tiles="cartodbpositron")

#faire une carte des départements avec le nombre de féminicides par département
chloropleth = folium.Choropleth(
    geo_data=json_dep,
    name="choropleth",
    data=df_total_dep,
    columns=["dep_nom", "feminicide_per_100k"],
    key_on="feature.properties.nom",  # correspond au champ du geojson
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Nombre de féminicides par département pour 100 000 habitants par an ",
)

chloropleth.geojson.add_child(
    folium.features.GeoJsonTooltip(['Légende'], labels=False))

chloropleth.add_to(Carte)

#rajouter une légende pour les données manquantes
import branca
legend_nan = """
<div style="
    position: fixed; 
    top: 50px; right: 50px; width: 220px; height: 50px; 
    border:2px solid grey; z-index:9999; font-size:14px;
    background-color:white; opacity:0.9;
    ">
    <p style="margin:5px;">
        <span style="background-color:black;
             opacity:0.7;
             border:1px solid black;
             display:inline-block;
             width:20px;height:20px;
             margin-right:5px;"></span>
        Données manquantes
    </p>
</div>
"""
Carte.get_root().html.add_child(folium.Element(legend_nan))

st_folium(Carte, width=800, height=600)




