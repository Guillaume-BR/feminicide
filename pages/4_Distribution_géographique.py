import streamlit as st
import pandas as pd
import os
import folium
from streamlit_folium import st_folium
import geopandas as gpd
from utils.functions import load_global_css

load_global_css()

#definir working directory
wd = os.path.dirname(os.path.abspath(__file__))

#charger les données
fem_path = os.path.join(wd, "..", "data", "processed", "feminicide_2022_2025.csv")
df_fem = pd.read_csv(fem_path)

st.title("🌍 La zone géographique a-t-elle un impact ?") 

#charger les données des départements des féminicides par département
json_dep = gpd.read_file(os.path.join(wd, "..", "data", "processed", "departements_feminicide.geojson"))
df_total_dep = pd.read_csv(os.path.join(wd, "..", "data", "processed", "df_total_dep.csv"))


# Créer la carte
location = [47, 3.2]  # centre de la France
zoom = 6
Carte = folium.Map(location=location, zoom_start=zoom, tiles="cartodbpositron")

#faire une carte des départements avec le nombre de féminicides par département
chloropleth = folium.Choropleth(
    geo_data=json_dep,
    data=df_total_dep,
    columns=["dep_nom", "feminicide_per_100k"],
    key_on="feature.properties.nom",  # correspond au champ du geojson
    fill_color="RdPu",
    fill_opacity=0.7,
    line_opacity=1,
    legend_name="Féminicides pour 100 000 habitants/an",
    highlight=True
)

chloropleth.geojson.add_child(
    folium.features.GeoJsonTooltip(['Légende'], labels=False))

chloropleth.add_to(Carte)

#rajouter une légende pour les données manquantes
import branca
legend_nan = """
<div style="
    position: fixed; 
    top: 50px; 
    right: 200px; 
    width: 200px; 
    height: 50px; 
    z-index:9999; 
    font-size:14px;
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

st_folium(Carte, width=800, height=500)

st.markdown("""
Cette carte a été construite à partir de données recensant les féminicides de 2022 à 2025.  
Il y a donc certains départements où l'on manque de données afin de pouvoir calculer le **taux de féminicides par 100 000 habitants et par an**.  
Ces départements sont indiqués en **noir** sur la carte.  

On note qu'il n'y a pas nécessairement de lien entre la nature de certains départements — *ruraux, urbains, très peuplés, moins peuplés* — et le nombre de féminicides rapportés à la population.  

Toutefois, pour les départements peu peuplés comme par exemple les **Hautes-Alpes** ou la **Corse du Nord**, le taux de féminicides peut être surestimé car un seul féminicide dans un département peu peuplé peut faire augmenter fortement ce taux.  

On observe enfin que le centre de la France semble moins touché que le reste du territoire, mais il est difficile d'en tirer des conclusions pertinentes si ce n'est que **chaque femme tuée est un féminicide de trop**.
""")