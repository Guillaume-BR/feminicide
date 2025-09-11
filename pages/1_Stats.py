import streamlit as st
import pandas as pd
import os

st.title("📊 Statistiques")

#definir working directory
wd = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(wd, "..", "data", "processed", "feminicide_2022_2025.csv")
df_fem = pd.read_csv(data_path)

# Statistiques simples
df_fem["année"] = pd.to_datetime(df_fem["date"], errors="coerce").dt.year
stats = df_fem["année"].value_counts().sort_index()
st.bar_chart(stats)