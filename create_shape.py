import pandas as pd
import geopandas as gpd
import folium
from folium.features import DivIcon

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

# Wyświetlenie pierwszych kilku rekordów po połączeniu danych
print(gdf.head())

# Tworzenie mapy
m = folium.Map(location=[52.237049, 21.017532], zoom_start=6)

# Dodanie warstw do mapy
age_groups = ['Male_0', 'Female_0']

for age_group in age_groups:
    choropleth = folium.Choropleth(
        geo_data=gdf,
        name=age_group,
        data=gdf,
        columns=['Voivodship', age_group],
        key_on='feature.properties.Voivodship',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f'Population of {age_group.replace("_", " ")}'
    )
    choropleth.add_to(m)
    
    # Tworzenie grupy warstw dla etykiet
    label_layer = folium.FeatureGroup(name=f'{age_group} Labels')
    
    # Dodanie etykiet do grupy warstw
    for _, row in gdf.iterrows():
        folium.map.Marker(
            [row.geometry.centroid.y, row.geometry.centroid.x],
            icon=DivIcon(
                icon_size=(150,36),
                icon_anchor=(0,0),
                html=f'<div style="font-size: 10pt">{int(row[age_group])}</div>',
            )
        ).add_to(label_layer)
    
    label_layer.add_to(m)

# Dodanie warstwy kontrolnej
folium.LayerControl().add_to(m)

# Zapisanie mapy do pliku HTML
m.save('C:/Projekty/Life Expect/demographic_map.html')
