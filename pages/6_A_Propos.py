import streamlit as st

st.title("ℹ️ À propos")
st.markdown(
    """
Cette application a été développée pour sensibiliser le public au fléau des féminicides en France
et pour fournir des informations statistiques basées sur les données collectées de 2022 à 2025.
            
Les données utilisées proviennent de sources publiques et ont été traitées pour garantir leur exactitude et leur pertinence : 
- Décompte des féminicides en France : [https://www.data.gouv.fr/datasets/decompte-et-recensement-des-feminicides/](https://www.data.gouv.fr/datasets/decompte-et-recensement-des-feminicides/)
- Données des communes françaises : [https://www.data.gouv.fr/datasets/communes-france-1/](https://www.data.gouv.fr/datasets/communes-france-1/)
- Répartition par âge de la population : [https://www.insee.fr/fr/statistiques/2381474](https://www.insee.fr/fr/statistiques/2381474)
- Cartes des départements : [https://france-geojson.gregoiredavid.fr/repo/departements.geojson](https://france-geojson.gregoiredavid.fr/repo/departements.geojson)
"""
)

st.markdown(
    """Projet réalisé avec : 
 - **Streamlit** : pour la partie front-end, 
 - **Folium** : pour la cartographie, 
 - **Plotly** : pour les graphiques.
 - **Geopy** : pour la géocodification des adresses,
 - **OpenAI** : pour la classification des liens entre la victime et le meurtrier.e.
"""
)
