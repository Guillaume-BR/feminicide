import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
import os
from folium.plugins import HeatMap

#definir working directory
os.chdir('C:/Users/ghirg/Documents/GitHub/feminicide')

def load_data(file_path):
    """Load data from a CSV file."""
    return pd.read_csv(file_path)

df_2022 = load_data(./data/feminicide_2022.csv)
def visualize_data(df):
    """Visualize the data."""
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['value'])
    plt.title('Data over Time')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.show()

def create_map(df):
    """Create a folium map with heatmap."""
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=6)
    HeatMap(data=df[['latitude', 'longitude', 'value']].values, radius=15).add_to(m)
    return m
