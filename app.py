import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# Supposons df_fem contient latitude, longitude, age, prenom, date, commune, departement

# S'assurer que la colonne 'date' est datetime
df_fem['date'] = pd.to_datetime(df_fem['date'])

# Décalage léger des points doublons pour qu'ils ne se chevauchent pas
coord_counts = df_fem.groupby(['latitude', 'longitude']).size().to_dict()
coord_seen = {}

latitudes, longitudes = [], []
for idx, row in df_fem.iterrows():
    lat, lon = row['latitude'], row['longitude']
    if coord_counts[(lat, lon)] > 1:
        count = coord_seen.get((lat, lon), 0)
        angle = 2 * np.pi * count / coord_counts[(lat, lon)]
        offset = 0.002  # ~200m
        lat += offset * np.cos(angle)
        lon += offset * np.sin(angle)
        coord_seen[(row['latitude'], row['longitude'])] = count + 1
    latitudes.append(lat)
    longitudes.append(lon)

df_fem['lat_jitter'] = latitudes
df_fem['lon_jitter'] = longitudes

# Créer la carte avec animation par date
fig = px.scatter_mapbox(
    df_fem,
    lat='lat_jitter',
    lon='lon_jitter',
    hover_name='prenom',
    hover_data={'age':True, 'date':True, 'commune':True, 'departement':True},
    color='age',          # optionnel : colorer par âge
    size_max=15,
    zoom=6,
    mapbox_style='open-street-map',
    animation_frame=df_fem['date'].dt.strftime('%Y-%m-%d')  # animation par date
)

# Afficher dans Streamlit
st.plotly_chart(fig, use_container_width=True)


