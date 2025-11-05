#creer timeline où les pointeurs arrivent les uns après les autres selon la date
import folium
import pandas as pd
import numpy as np
from folium.plugins import TimestampedGeoJson
import plotly.express as px

def timeline_map_jitter(df):
    """
    Create a Folium map displaying a timeline of markers with jitter for overlapping points.

    This function generates an interactive map using Folium, where each marker represents an event
    (e.g., feminicide) at a specific location and date. If multiple events share the same coordinates,
    their markers are slightly offset ("jittered") to avoid overlap. The map includes a timeline slider
    to visualize the events chronologically.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the following columns:
            - 'latitude': float, latitude of the event
            - 'longitude': float, longitude of the event
            - 'date': datetime or str, date of the event
            - 'prenom': str, first name of the victim
            - 'age': float or int, age of the victim
            - 'meurtrier': str, relationship to the perpetrator
            - 'commune': str, commune of the event
            - 'departement': str, department of the event
            - 'lien_instagram': str or NaN, Instagram link (optional)

    Returns
    -------
    folium.Map
        Folium map object with timeline and jittered markers.

    Notes
    -----
    - Markers are offset by a small distance (~200m) if multiple events share the same coordinates.
    - Each marker includes a popup with event details and an optional Instagram link.
    - The timeline slider allows users to explore events by date.
    """
    
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
    """
    Génère un graphique à barres représentant la distribution des tranches d'âge en pourcentage, 
    en distinguant les types d'événements (par exemple, féminicides vs population globale).
    Paramètres
    ----------
    df : pandas.DataFrame
        DataFrame contenant les données à visualiser, avec au moins les colonnes "Tranche d'âge", "Pourcentage" et "Type".
    age_stats : pandas.DataFrame
        DataFrame contenant les statistiques d'âge, utilisé pour définir la plage de l'axe des ordonnées.
    Retourne
    --------
    fig : plotly.graph_objs._figure.Figure
        Objet Figure Plotly représentant le graphique à barres.
    """
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


def load_global_css():
    with open("styles/light.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)