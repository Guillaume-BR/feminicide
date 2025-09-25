#creer timeline où les pointeurs arrivent les uns après les autres selon la date
import folium
import pandas as pd
import numpy as np
from folium.plugins import TimestampedGeoJson
import plotly.express as px

def timeline_map_jitter(df):
    """Create a folium map with a timeline of markers and slight offset for overlapping points."""
    # Centrer la carte
    m = folium.Map(location=[46.9, 3.2], zoom_start=6)
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
                "popup": (
                        f"{row['prenom']} "
                        f"{int(row['age']) if pd.notnull(row['age']) else 'Non nommée'} ans, "
                        f"tuée par son {row['meurtrier']} le {row['date'].strftime('%Y-%m-%d')}<br>"
                        f"{row['commune']}, {row['departement']}<br>"
                        f"<a href='{row['lien_instagram']}' target='_blank'>Lien Instagram</a>" if pd.notnull(row['lien_instagram']) else ""
                    ),
                "id" : "house",
                "icon": "marker",
                "iconstyle": {
                    "iconUrl": "https://raw.githubusercontent.com/Guillaume-BR/feminicide/main/pictures/icone_feminicide.png",  # chemin relatif vers l'image
                    "iconSize": [25, 25],         # taille de l'icône en pixels
                    "iconAnchor": [12, 12],       # point d'ancrage de l'icône
                    },
                }
            }
        features.append(feature)
    # Ajouter la timeline
    TimestampedGeoJson(
        {"type": "FeatureCollection", "features": features},
        period="P1D",
        add_last_point=True,
        auto_play=True,
        loop=False,
        max_speed=50,
        loop_button=True,
        date_options="YYYY-MM-DD",
        time_slider_drag_update=True
    ).add_to(m)
    return m


def barplot_age_distribution(df, age_stats):
    fig = px.bar(
        df,
        x="Tranche d'âge",
        y="Pourcentage",
        color="Type",
        barmode="group",  # barres côte à côte
        text="Pourcentage",
        labels={"Tranche d'âge":"Tranche d'âge (ans)", "Pourcentage":"Pourcentage (%)"},
        width=800,
        height=500
    )

    # Afficher les valeurs sur les barres
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")

    # Améliorer la lisibilité des labels X
    fig.update_layout(xaxis_tickangle=-45, yaxis_range=[0, age_stats[["Fréquence des féminicides (%)","Population globale (%)"]].max()*1.2])
    return fig