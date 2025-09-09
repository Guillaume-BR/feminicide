import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
import os
from folium.plugins import HeatMap
from folium.plugins import MarkerCluster
from folium.plugins import TimestampedGeoJson
import streamlit as st


#definir working directory
os.chdir('C:/Users/ghirg/Documents/GitHub/feminicide')

df_fem = pd.read_csv('./data/processed/feminicide_2022_2025.csv')

st.title('Visualisation des féminicides en France (2022-2025)')
st.write('Cette application visualise les données des féminicides en France entre 2022 et 2025.')

def create_map(df):
    """Create a folium map with heatmap."""
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=6)
    HeatMap(data=df[['latitude', 'longitude', 'frequence_par_habitant']].values, radius=15).add_to(m)
    return m

#mettre un pointeur sur la carte pour chaque feminicide et quand il y en plusieurs avec le même point, les décaler un peu
def create_map_with_markers(df):
    """Create a folium map with clustered markers."""
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=6)
    marker_cluster = MarkerCluster().add_to(m)
    
    for idx, row in df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"{row['prenom']} {row['age']} - {row['date']} - "
                  f"{row['commune_sans_accent']}, {row['departement_sans_accent']}"
        ).add_to(marker_cluster)
    return m

#creer timeline où les pointeurs arrivent les uns après les autres selon la date
def create_timeline_map_jitter(df):
    """Create a folium map with a timeline of markers and slight offset for overlapping points."""
    
    # Centrer la carte
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=6)
    
    # Assurer que la colonne 'date' est en datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Compter les doublons de coordonnées
    coord_counts = df.groupby(['latitude', 'longitude']).size().to_dict()
    coord_seen = {}
    
    features = []
    for _, row in df.sort_values('date').iterrows():
        lat, lon = row['latitude'], row['longitude']
        
        # Décalage léger si plusieurs points au même endroit
        if coord_counts[(lat, lon)] > 1:
            count = coord_seen.get((lat, lon), 0)
            angle = 2 * np.pi * count / coord_counts[(lat, lon)]
            offset = 0.002  # environ 200m
            lat += offset * np.cos(angle)
            lon += offset * np.sin(angle)
            coord_seen[(row['latitude'], row['longitude'])] = count + 1
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat],
            },
            "properties": {
                "time": row['date'].strftime("%Y-%m-%d"),
                "popup": f"{row['prenom']} {int(row['age']) if pd.notnull(row['age']) else 'Non nommée'} ans  - {row['date'].strftime('%Y-%m-%d')} - "
                         f"{row['commune']}, {row['departement']}",
                "icon": "circle",
                "iconstyle": {
                    "fillColor": "red",
                    "fillOpacity": 0.6,
                    "stroke": "true",
                    "radius": 7
                },
            },
        }
        features.append(feature)
    
    # Ajouter la timeline
    TimestampedGeoJson(
        {"type": "FeatureCollection", "features": features},
        period="P1D",
        add_last_point=True,
        auto_play=True,
        loop=False,
        max_speed=10,
        loop_button=True,
        date_options="YYYY-MM-DD",
        time_slider_drag_update=True
    ).add_to(m)
    
    return m

timeline_map = create_timeline_map_jitter(df_fem)
timeline_map.save("feminicide_timeline.html")

#intégrer la carte dans streamlit
st.components.v1.html(timeline_map._repr_html_(), width=800, height=600)


