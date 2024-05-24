import pandas as pd
import geopandas as gpd
import plotly.express as px
import h3
from shapely.geometry import Polygon
import os
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Wczytanie danych demograficznych
file_path = 'C:/Projekty/Life Expect/table_b_life_expectancy_in_poland_by_voivodships_in_2022.xlsx'
df = pd.read_excel(file_path)

# Usuwamy pierwszą kolumnę
df = df.iloc[:, 1:]

# Wybieramy tylko wiersze od 0 do 21 (22 wiersze łącznie)
df_total = df.iloc[5:22, :]

# Zakładamy, że kolumny 3, 4, 5, 6 zawierają dane o mężczyznach
df_men = df_total.iloc[:, [0, 1, 2, 3, 4, 5]]
# Zmieniamy nazwy kolumn dla mężczyzn
df_men.columns = ['Voivodship', 'Male_0', 'Male_15', 'Male_30', 'Male_45', 'Male_60']

# Zakładamy, że kolumny 6, 7, 8, 9, 10 zawierają dane o kobietach
df_women = df_total.iloc[:, [0, 6, 7, 8, 9, 10]]
# Zmieniamy nazwy kolumn dla kobiet
df_women.columns = ['Voivodship', 'Female_0', 'Female_15', 'Female_30', 'Female_45', 'Female_60']

# Łączymy dane dla mężczyzn i kobiet
df_combined = pd.merge(df_men, df_women, on='Voivodship')

# Wyświetlenie unikalnych wartości w kolumnie 'Voivodship' w danych demograficznych
print("Voivodship values in demographic data:")
print(df_combined['Voivodship'].unique())

# Wczytanie pliku shapefile z granicami administracyjnymi Polski
shapefile_path = 'C:/Projekty/Life Expect/Shape Files/A01_Granice_wojewodztw.shp'
gdf = gpd.read_file(shapefile_path)

# Wyświetlenie dostępnych kolumn w pliku shapefile
print("Columns in shapefile data:")
print(gdf.columns)

# Wyświetlenie unikalnych wartości w kolumnie 'JPT_NAZWA_' w pliku shapefile
print("Voivodship values in shapefile data:")
print(gdf['JPT_NAZWA_'].unique())

# Słownik mapujący niepoprawne nazwy na poprawne
voivodship_mapping = {
    'warmiÅ\x84sko-mazurskie': 'Warmińsko-Mazurskie',
    'opolskie': 'Opolskie',
    'Å\x9bwiÄ\x99tokrzyskie': 'Świętokrzyskie',
    'lubuskie': 'Lubuskie',
    'pomorskie': 'Pomorskie',
    'Å\x82Ã³dzkie': 'Łódzkie',
    'dolnoÅ\x9blÄ\x85skie': 'Dolnośląskie',
    'zachodniopomorskie': 'Zachodniopomorskie',
    'Å\x9blÄ\x85skie': 'Śląskie',
    'mazowieckie': 'Mazowieckie',
    'maÅ\x82opolskie': 'Małopolskie',
    'lubelskie': 'Lubelskie',
    'kujawsko-pomorskie': 'Kujawsko-Pomorskie',
    'podlaskie': 'Podlaskie',
    'wielkopolskie': 'Wielkopolskie',
    'podkarpackie': 'Podkarpackie'
}

# Poprawienie nazw województw w pliku shapefile
gdf['JPT_NAZWA_'] = gdf['JPT_NAZWA_'].map(voivodship_mapping)

# Sprawdzenie, czy nazwy zostały poprawnie zmapowane
print("Corrected Voivodship values in shapefile data:")
print(gdf['JPT_NAZWA_'].unique())

# Zmieniamy nazwę kolumny na 'Voivodship'
gdf = gdf.rename(columns={'JPT_NAZWA_': 'Voivodship'})

# Łączenie danych demograficznych z danymi geograficznymi
gdf = gdf.merge(df_combined, on='Voivodship')

# Generowanie heksagonów dla całej Polski
resolution = 5  # Ustawienie rozdzielczości heksagonów (zmniejszenie wartości zwiększa rozmiar heksagonów)

# Tworzenie geometrii heksagonów
poland_boundary = gdf.unary_union
# Tworzenie geometrii heksagonów z buforem
buffer_distance = -0.001  # Ustawienie odległości bufora od granic Polski (zmniejszenie wartości zwiększa odległość)
hexagons = []
hex_indices = h3.polyfill(poland_boundary.__geo_interface__, resolution, geo_json_conformant=True)
for h in hex_indices:
    hex_boundary = h3.h3_to_geo_boundary(h, geo_json=True)
    hex_polygon = Polygon(hex_boundary).buffer(buffer_distance)
    hexagons.append({
        'geometry': hex_polygon,
        'h3_index': h
    })
hex_gdf = gpd.GeoDataFrame(hexagons, crs="EPSG:4326")

# Przypisanie wartości do heksagonów
hex_gdf = gpd.sjoin(hex_gdf, gdf, how='left', op='intersects')
hex_gdf = hex_gdf.dropna(subset=['Voivodship'])

# Tworzenie katalogu na pliki graficzne
output_dir = 'C:/Projekty/Life Expect/hex_maps_interactive'
os.makedirs(output_dir, exist_ok=True)

# Mapowanie nazw kolumn na bardziej czytelne nazwy
age_group_labels = {
    'Male_0': 'Oczekiwana długość życia mężczyzn w wieku 0 lat',
    'Male_15': 'Oczekiwana długość życia mężczyzn w wieku 15 lat',
    'Male_30': 'Oczekiwana długość życia mężczyzn w wieku 30 lat',
    'Male_45': 'Oczekiwana długość życia mężczyzn w wieku 45 lat',
    'Male_60': 'Oczekiwana długość życia mężczyzn w wieku 60 lat',
    'Female_0': 'Oczekiwana długość życia kobiet w wieku 0 lat',
    'Female_15': 'Oczekiwana długość życia kobiet w wieku 15 lat',
    'Female_30': 'Oczekiwana długość życia kobiet w wieku 30 lat',
    'Female_45': 'Oczekiwana długość życia kobiet w wieku 45 lat',
    'Female_60': 'Oczekiwana długość życia kobiet w wieku 60 lat'
}

colorscale = [[0, "#dad66f"], [1, "darkgreen"]]

# Generowanie interaktywnych map heksagonalnych z tooltipami
for age_group, label in age_group_labels.items():
    hex_gdf[age_group] = hex_gdf[age_group].astype(float)

    # Use the colorscale in the figure
    fig = px.choropleth_mapbox(
        hex_gdf, geojson=hex_gdf.geometry, 
        locations=hex_gdf.index, color=age_group,
        hover_name="Voivodship", 
        mapbox_style="white-bg", 
        zoom=6, center = {"lat": 52.069167, "lon": 19.480556},
        opacity=0.9, 
        labels={age_group: label},
        hover_data={'Voivodship': True, 'h3_index': False},
        color_continuous_scale=colorscale  # Use the colorscale here
    )
    fig.update_traces(marker_line=dict(width=3, color='white'))  # Dodanie białych linii między heksagonami
    fig.update_layout(coloraxis_showscale=False)
    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        )
    )
    fig.update_layout(
        legend=dict(
            font=dict(
                size=20  # Increase this value to increase the size of the text in the legend
            )
        )
    )
    cmap = mcolors.LinearSegmentedColormap.from_list("mycmap", colorscale)  # Utworzenie mapy kolorów


    # Dodanie legendy z kropkami kolorów
    min_val = hex_gdf[age_group].min()
    max_val = hex_gdf[age_group].max()
    for i in np.linspace(min_val, max_val, 5):
        normalized_i = (i - min_val) / (max_val - min_val)  # Normalizacja do zakresu 0-1
        color = cmap(normalized_i)  # Interpolacja koloru
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=400, color='rgba'+str(color)),  # wielkość kropki i kolor
            legendgroup="Life Expectancy", name=f"{round(i, 2)}",  # Round to 2 decimal places
            showlegend=True
        ))
    # Zapisanie do pliku HTML
    fig.write_html(f"{output_dir}/{label}.html")

print("Interaktywne mapy heksagonalne zostały zapisane w katalogu: hex_maps_interactive")