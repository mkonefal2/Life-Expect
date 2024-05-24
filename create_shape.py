import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import h3
from shapely.geometry import Polygon
import os
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

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

# Zmieniamy nazwy kolumn na bardziej czytelne
colors = ["#dad66f", "darkgreen"]
# Tworzenie niestandardowej mapy kolorów
cmap = LinearSegmentedColormap.from_list("mycmap", colors)

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
output_dir = 'C:/Projekty/Life Expect/hex_maps'
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

# Generowanie i zapisywanie plików graficznych

for age_group, label in age_group_labels.items():
    vmin = df_combined[age_group].min()
    vmax = df_combined[age_group].max()
    
    fig, ax = plt.subplots(1, 1, figsize=(20, 20)) 
    hex_gdf.boundary.plot(ax=ax, linewidth=2, color='white', alpha=0.0)
    hex_gdf.plot(column=age_group, cmap=cmap, linewidth=2.0, ax=ax, edgecolor='#FFFFFF', legend=False)

    # Dostosowanie proporcji osi
    ax.set_aspect('equal', 'box')

    # Ustawienie zakresu osi X i Y
    ax.set_xlim([hex_gdf.bounds.minx.min(), hex_gdf.bounds.maxx.max()])
    ax.set_ylim([hex_gdf.bounds.miny.min(), hex_gdf.bounds.maxy.max()])
    # Ustawienie zakresu osi Y
    y_min = hex_gdf.bounds.miny.min()
    y_max = hex_gdf.bounds.maxy.max()
    y_range = y_max - y_min
    ax.set_ylim([y_min - 0.1 * y_range, y_max + 0.01 * y_range])
    # Dodanie legendy z kropkami
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.5)

    legend_labels = np.linspace(vmin, vmax, num=10)
    for value in legend_labels:
        cax.scatter([], [], color=sm.to_rgba(value), label=f"{value:.2f}", s=2400)  # Zwiększenie wielkości kropek

    # Położenie legendy tak aby kropki nie wchodziły na siebie, tytuł nie wchodził na legendę
    cax.legend(frameon=False, loc='center left', fontsize='15', labelspacing=2, borderpad=2, handletextpad=2, borderaxespad=2, handlelength=0, bbox_to_anchor=(-1., 0.5))
    cax.axis('off')
    # Dodanie tytułu:
    fig.suptitle(label, x=0.5, y=0.95, fontsize=20)

    # Dostosowanie proporcji osi
    ax.set_aspect('auto')

    ax.axis('off')
    plt.savefig(f"{output_dir}/{label}.png")
    plt.close(fig)

    print(f"Mapy heksagonalne zostały zapisane w katalogu: {output_dir}")