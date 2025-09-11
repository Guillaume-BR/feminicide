#creer timeline où les pointeurs arrivent les uns après les autres selon la date
import folium
import pandas as pd
import numpy as np
from folium.plugins import TimestampedGeoJson


def timeline_map_jitter(df):
    """Create a folium map with a timeline of markers and slight offset for overlapping points."""
    # Centrer la carte
    m = folium.Map(location=[46.87119718803805, 3.154828089876449], zoom_start=6)
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
        max_speed=50,
        loop_button=True,
        date_options="YYYY-MM-DD",
        time_slider_drag_update=True
    ).add_to(m)
    return m