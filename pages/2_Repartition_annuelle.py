import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

#definir working directory
wd = os.path.dirname(os.path.abspath(__file__))

#charger les données
fem_path = os.path.join(wd, "..", "data", "processed", "feminicide_2022_2025.csv")
df_fem = pd.read_csv(fem_path)

#Etude par années
st.title("📊 Répartition annuelle des féminicides")

df_fem["année"] = pd.to_datetime(df_fem["date"], errors="coerce").dt.year
nb_fem = df_fem["année"].value_counts().sort_index()

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(nb_fem.index.astype(int), nb_fem.values, color="#1f77b4")
ax.set_xlabel("Année")
ax.set_ylabel("Nombre de féminicides")
ax.set_xticks(nb_fem.index.astype(int))
for x, y in zip(nb_fem.index.astype(int), nb_fem.values):
    ax.text(x, y, str(y), ha="center", va="bottom")
plt.tight_layout()

# afficher dans Streamlit
st.pyplot(fig)

st.plotly_chart(fig_annee)

st.write("Le nombre de féminicides est malheureusement constant au cours du temps. La baisse observée en 2025 vient seulment du fait que les données s'arrêtent en août 2025. " \
"Il y a fort à parier que le nombre total de féminicides en 2025 sera similaire aux années précédentes.")