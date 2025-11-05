import streamlit as st
import pandas as pd
import os
from utils.functions import barplot_age_distribution

#definir working directory
wd = os.path.dirname(os.path.abspath(__file__))

#charger les données
fem_path = os.path.join(wd, "..", "data", "processed", "feminicide_2022_2025.csv")
df_fem = pd.read_csv(fem_path)

#Statistique par tranche d'âge
st.title("📊 Répartition des féminicides par tranche d'âge")

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



st.markdown("""Avant 20 ans, la proportion de féminicides est très inférieure à la population globale. Ensuite malheureusement, le pourcentage de féminicides devient supérieur à la population glabale, jusqu'à 65 ans.          
On peut émettre une hypothèse sur le fait que les femmes se mettent en couple à partir de 20 ans et le risque de féminicide augmente avec la vie de couple.
Toutefois, ne connaissant pas le ou les motifs de ces meurtres, nous ne pouvons aller plus loin dans les interprétations.
            """)