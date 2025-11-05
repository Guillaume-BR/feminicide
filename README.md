# Féminicide

Le but de ce projet est de continuer à sensibiliser le public aux violences faites aux femmes et en particulier les féminicides. Notre société a encore du chemin à faire pour parvenir à l'égalité entre les femmes et les hommes. 👩 = 👨

## Donnnées utilisées

- Données des différents féminicides : [Féminicides en France](https://www.data.gouv.fr/datasets/decompte-et-recensement-des-feminicides/)
- Données des communes françaises : [Communes et villes de France](https://www.data.gouv.fr/datasets/communes-et-villes-de-france-en-csv-excel-json-parquet-et-feather/)
- Données pour le découpage des départements : [Départements français](https://france-geojson.gregoiredavid.fr/repo/departements.geojson)
- Répartition par âge de la population : [INSEE - Répartition par âge](https://www.insee.fr/fr/statistiques/2381474)

## Packages utilisés
- Nettoyage et traitement des données avec **Pandas**.
- Géocodification des adresses avec **Geopy**.
- Visualisation des données avec **Folium** et **Plotly**.
- Création de l'application web avec **Streamlit**.
- Classification des liens entre la victime et le meurtrier.e avec **OpenAI**.

## Méthodologie
1. **Collecte des données :** Récupération des données sur les féminicides en France de 2022 à 2025 à partir de sources fiables.
2. **Nettoyage des données :** Suppression des doublons, gestion des valeurs manquantes, et formatage des données.
3. **Jointure des données :** Fusion des données des féminicides avec les données des communes pour obtenir des informations géographiques.
4. **Géocodification :** Utilisation de la bibliothèque Geopy et de son API pour obtenir les coordonnées géographiques (latitude et longitude) pour les jointures défaillantes (NaN).
5. **Utilisation de l'API OpenAI :** Classification des liens entre la victime et le meurtrier.e.
6. **Visualisation des données :** Création de graphiques et de cartes interactives pour représenter les données : Timeline, répartition par âge, lien avec la victime, répartition géographique.
7. **Déploiement de l'application :** Utilisation de Streamlit pour créer une page web permettant aux utilisateurs d'explorer les données.