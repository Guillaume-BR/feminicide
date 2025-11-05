import pandas as pd
import os
import streamlit as st
from streamlit_folium import st_folium  
from utils.functions import timeline_map_jitter
import plotly.express as px

#definir working directory
wd = os.path.dirname(os.path.abspath(__file__))

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Titre principal ---
st.set_page_config(page_title="Le fléau des Féminicides", page_icon="♀️")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&family=Playfair+Display:wght@500&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)


#charger les données
data_path = os.path.join(wd, "data", "processed", "feminicide_2022_2025.csv")
df_fem = pd.read_csv(data_path)

# -------- PAGE ACCUEIL --------
st.title('Les féminicides en France de 2022 à 2025')
st.markdown('En France, **tous les trois jours**, une femme est assassinée.')
st.markdown("Merci au collectif #NousToutes pour leur travail de recensement et de sensibilisation aux féminicides en France." )
st.markdown("N'hésitez pas à répondre ou à consulter le résultat de leurs [enquêtes](https://www.noustoutes.org/enquetes/)."
)

timeline_map = timeline_map_jitter(df_fem)

#intégrer la carte dans streamlit
st_folium(timeline_map, width=800, height=600)

