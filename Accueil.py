import pandas as pd
import os
import streamlit as st
from streamlit_folium import st_folium  
from utils.functions import timeline_map_jitter

#definir working directory
wd = os.path.dirname(os.path.abspath(__file__))

# Config de la page
st.set_page_config(
    page_title="Dashboard Féminicides",
    page_icon="🗺️",
    layout="wide"
)

# Config globale
st.set_page_config(page_title="Dashboard Féminicides", page_icon="🗺️", layout="wide")

#charger les données
data_path = os.path.join(wd, "data", "processed", "feminicide_2022_2025.csv")
df_fem = pd.read_csv(data_path)

# -------- PAGE ACCUEIL --------
st.title('Les féminicides en France de 2022 à 2025')
st.write('Les données recensées en France métropolitaine et outre-mer.')

timeline_map = timeline_map_jitter(df_fem)
#intégrer la carte dans streamlit
st_folium(timeline_map, width=800, height=600)
