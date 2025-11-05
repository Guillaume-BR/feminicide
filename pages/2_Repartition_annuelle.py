import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# Définir le working directory
wd = os.path.dirname(os.path.abspath(__file__))

# Charger les données
fem_path = os.path.join(wd, "..", "data", "processed", "feminicide_2022_2025.csv")
df_fem = pd.read_csv(fem_path)

# Étude par années
st.title("📊 Répartition annuelle des féminicides")

# Extraire l'année
df_fem["année"] = pd.to_datetime(df_fem["date"], errors="coerce").dt.year

# Compter par année et s’assurer que toutes les années 2022 à 2025 sont présentes
annees = [2022, 2023, 2024, 2025]
nb_fem = df_fem["année"].value_counts().reindex(annees, fill_value=0)

# Créer le barplot
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(nb_fem.index, nb_fem.values, color="#1f77b4")
ax.set_xlabel("Année")
ax.set_ylabel("Nombre de féminicides")
ax.set_title("Répartition annuelle des féminicides (2022–2025)")

# Ajouter les valeurs sur les barres
for x, y in zip(nb_fem.index, nb_fem.values):
    ax.text(x, y + 0.5, str(y), ha="center", va="bottom")

ax.set_xticks(annees)
plt.tight_layout()

# Afficher dans Streamlit
st.pyplot(fig)

st.write("Le nombre de féminicides est malheureusement constant au cours du temps. La baisse observée en 2025 vient seulment du fait que les données s'arrêtent en août 2025. " \
"Il y a fort à parier que le nombre total de féminicides en 2025 sera similaire aux années précédentes.")