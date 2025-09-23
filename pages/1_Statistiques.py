import streamlit as st
import pandas as pd
import os
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import plotly.express as px
from utils.functions import barplot_age_distribution

#definir working directory
wd = os.path.dirname(os.path.abspath(__file__))

#charger les données
fem_path = os.path.join(wd, "..", "data", "processed", "feminicide_2022_2025.csv")
df_fem = pd.read_csv(fem_path)

st.title("📊 Existe-t-il des facteurs d'influence ?")

#Etude par années
st.markdown("<h2>Le nombre de féminicides dépend-il des années ?</h2>", unsafe_allow_html=True)

df_fem["année"] = pd.to_datetime(df_fem["date"], errors="coerce").dt.year
nb_fem = df_fem["année"].value_counts().sort_index()

fig_annee = px.bar(
    x=nb_fem.index,
    y=nb_fem.values,
    labels={"x": "Année", "y": "Nombre de féminicides"}
)

st.plotly_chart(fig_annee)

st.write("Le nombre de féminicides est malheureusement constant au cours du temps. La baisse observée en 2025 vient seulment du fait que les données s'arrêtent en août 2025. " \
"Il y a fort à parier que le nombre total de féminicides en 2025 sera similaire aux années précédentes.")


#Statistique par tranche d'âge
st.markdown("<h2>Cela dépend-il de l'âge ?</h2>", unsafe_allow_html=True)

#lire prop_femme.csv
prop_path = os.path.join(wd, "..", "data", "processed", "prop_femme.csv")
df_prop = pd.read_csv(prop_path,sep=';')

#nettoyer la colonne prop pour enlever les virgules et convertir en float
df_prop['prop'] = df_prop['prop'].str.replace(',', '.').astype(float)

# Définir les classes de 5 ans
bins = [0, 15] + list(range(20, 75, 5)) + [75,float('inf')]
labels = ["0-14"] + [f"{i}-{i+4}" for i in range(15, 75, 5)] + ["75+"]

# Découpage des âges
age_bins = pd.cut(df_fem["age"], bins=bins, right=False, labels=labels)

# Fréquences en %
age_stats = age_bins.value_counts().sort_index()
age_stats = (age_stats / age_stats.sum() * 100).round(1)
age_stats = age_stats.reset_index()
age_stats = pd.concat([age_stats, df_prop["prop"]], axis=1)
age_stats.columns = ["Tranche d'âge", "Fréquence des féminicides (%)","Population globale (%)"]

# Création du graphique Plotly
df_long = age_stats.melt(
    id_vars="Tranche d'âge",
    value_vars=["Fréquence des féminicides (%)", "Population globale (%)"],
    var_name="Type",
    value_name="Pourcentage"
)

# créer le graphique
fig_total = barplot_age_distribution(df_long,age_stats)

# Afficher dans Streamlit
st.plotly_chart(fig_total, use_container_width=True)

st.write("On observe qu'avant 15 ans, les femmes sont heureusement peu touchées par les féminicides par rapport à leur proportion dans la population globale. " \
"Ensuite, il semble que les pourcentages de féminicides suivent la démographie globale. Pour s'en rendre compte, il est intéressant de regarder seulement à partir de 15 ans")

#On refait mais en enlevant les 0-14 ans
age_stat_15 = age_bins[age_bins != "0-14"]
age_stats_15 = age_stat_15.value_counts().sort_index()
age_stats_15 = age_stats_15.loc[age_stats_15.index != "0-14"]
age_stats_15 = (age_stats_15 / age_stats_15.sum() * 100).round(1)
age_stats_15 = age_stats_15.reset_index()

tot_path = os.path.join(wd, "..", "data", "processed", "tot_femme.csv")
df_tot = pd.read_csv(tot_path, sep=';', encoding='latin1')

#enlever la première ligne de df_tot qui correspond à 0-14 ans
df_tot = df_tot[df_tot['age'] != 'Moins de 15 ans']
df_tot['prop'] = df_tot['Femmes']/df_tot['Femmes'].sum() * 100
df_tot['prop'] = df_tot['prop'].round(1)
df_tot.reset_index(drop=True, inplace=True)

age_stats_15 = pd.concat([age_stats_15, df_tot["prop"]], axis=1,ignore_index=True)
age_stats_15.columns = ["Tranche d'âge", "Fréquence des féminicides (%)","Population globale (%)"]

# Création du graphique Plotly
df_long_15 = age_stats_15.melt(
    id_vars="Tranche d'âge",
    value_vars=["Fréquence des féminicides (%)", "Population globale (%)"],
    var_name="Type",
    value_name="Pourcentage"
)

# créer le graphique
fig_15 = barplot_age_distribution(df_long_15,age_stats_15)

# Afficher dans Streamlit
st.plotly_chart(fig_15, use_container_width=True)

st.write("Avant 20 ans, la proportion de féminicides est très inférieure à la population globale. Ensuite malheureusement, le pourcentage de féminicides devient supérieur à la population glabale, jusqu'à 65 ans." \
"On peut émettre une hypothèse sur le fait que les femmes se mettent en couple à partir de 20 ans et le risque de féminicide augmente avec la vie de couple."\
     " Toutefois, ne connaissant pas le ou les motifs de ces meurtres, nous ne pouvons aller plus loin dans les interprétations.")

st.markdown("<h2>La zone géographique a-t-elle un impact ?</h2>", unsafe_allow_html=True)

#charger les données des départements
json_dep = gpd.read_file(os.path.join(wd, "..", "data", "processed", "departements_feminicide.geojson"))

#charger les données des féminicides par département
df_total_dep = pd.read_csv(os.path.join(wd, "..", "data", "processed", "df_total_dep.csv"))


# Créer la carte
location = [47, 3.2]  # centre de la France
zoom = 6
Carte = folium.Map(location=location, zoom_start=zoom, tiles="cartodbpositron")

#faire une carte des départements avec le nombre de féminicides par département
chloropleth = folium.Choropleth(
    geo_data=json_dep,
    name="choropleth",
    data=df_total_dep,
    columns=["dep_nom", "feminicide_per_100k"],
    key_on="feature.properties.nom",  # correspond au champ du geojson
    fill_color="RdPu",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Féminicides pour 100 000 habitants/an",
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
### Analyse de la carte des féminicides

Cette carte a été construite à partir de données recensant les féminicides de 2022 à 2025.  
Il y a donc certains départements où l'on manque de données afin de pouvoir calculer le **taux de féminicides par 100 000 habitants et par an**.  
Ces départements sont indiqués en **noir** sur la carte.  

On note qu'il n'y a pas nécessairement de lien entre la nature de certains départements — *ruraux, urbains, très peuplés, moins peuplés* — et le nombre de féminicides rapportés à la population.  

Toutefois, pour les départements peu peuplés comme par exemple les **Hautes-Alpes** ou la **Corse du Nord**, le taux de féminicides peut être surestimé car un seul féminicide dans un département peu peuplé peut faire augmenter fortement ce taux.  

On observe enfin que le centre de la France semble moins touché que le reste du territoire, mais il est difficile d'en tirer des conclusions pertinentes.
""")