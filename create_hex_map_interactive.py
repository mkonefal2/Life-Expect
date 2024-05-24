import argparse
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

# Utwórz parser argumentów
parser = argparse.ArgumentParser(description='Create hex maps.')

# Dodaj argumenty
parser.add_argument('--shapefile_path', type=str, help='Path to the shapefile')
parser.add_argument('--output_dir', type=str, help='Output directory for hex maps')
parser.add_argument('--file_path', type=str, help='Path to the data file')

# Analizuj argumenty
args = parser.parse_args()

# Użyj argumentów
shapefile_path = args.shapefile_path
output_dir = args.output_dir
df = pd.read_excel(args.file_path)

# Remove the first column
df = df.iloc[:, 1:]

# Select only rows from 0 to 21 (22 rows in total)
df_total = df.iloc[5:22, :]

# Columns 3, 4, 5, 6 contain data about men
df_men = df_total.iloc[:, [0, 1, 2, 3, 4, 5]]
# Rename columns for men
df_men.columns = ['Voivodship', 'Male_0', 'Male_15', 'Male_30', 'Male_45', 'Male_60']

# Columns 6, 7, 8, 9, 10 contain data about women
df_women = df_total.iloc[:, [0, 6, 7, 8, 9, 10]]
# Rename columns for women
df_women.columns = ['Voivodship', 'Female_0', 'Female_15', 'Female_30', 'Female_45', 'Female_60']

# Combine data for men and women
df_combined = pd.merge(df_men, df_women, on='Voivodship')

# Display unique values in the 'Voivodship' column in demographic data
print("Voivodship values in demographic data:")
print(df_combined['Voivodship'].unique())

# Load shapefile with administrative boundaries of Poland
shapefile_path = 'C:/Projekty/Life Expect/Shape Files/A01_Granice_wojewodztw.shp'
gdf = gpd.read_file(shapefile_path)

# Display available columns in the shapefile
print("Columns in shapefile data:")
print(gdf.columns)

# Display unique values in the 'JPT_NAZWA_' column in the shapefile
print("Voivodship values in shapefile data:")
print(gdf['JPT_NAZWA_'].unique())

# Dictionary mapping incorrect names to correct ones
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

# Correct voivodship names in the shapefile
gdf['JPT_NAZWA_'] = gdf['JPT_NAZWA_'].map(voivodship_mapping)

# Check if names were correctly mapped
print("Corrected Voivodship values in shapefile data:")
print(gdf['JPT_NAZWA_'].unique())

# Rename the column to 'Voivodship'
gdf = gdf.rename(columns={'JPT_NAZWA_': 'Voivodship'})

# Merge demographic data with geographic data
gdf = gdf.merge(df_combined, on='Voivodship')

# Generate hexagons for the entire Poland
resolution = 5  # Set hexagon resolution (decreasing value increases hexagon size)

# Create hexagon geometry
poland_boundary = gdf.unary_union
# Create hexagon geometry with buffer
buffer_distance = -0.001  # Set buffer distance from Poland's borders (decreasing value increases distance)
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

# Assign values to hexagons
hex_gdf = gpd.sjoin(hex_gdf, gdf, how='left', op='intersects')
hex_gdf = hex_gdf.dropna(subset=['Voivodship'])


# Map column names to more readable names
age_group_labels = {
    'Male_0': 'Life expectancy of men',
    'Male_15': 'Life expectancy of men at age 15',
    'Male_30': 'Life expectancy of men at age 30',
    'Male_45': 'Life expectancy of men at age 45',
    'Male_60': 'Life expectancy of men at age 60',
    'Female_0': 'Life expectancy of women',
    'Female_15': 'Life expectancy of women at age 15',
    'Female_30': 'Life expectancy of women at age 30',
    'Female_45': 'Life expectancy of women at age 45',
    'Female_60': 'Life expectancy of women at age 60'
}

colorscale = [[0, "#dad66f"], [1, "darkgreen"]]

# Generate interactive hexagonal maps with tooltips
for age_group, label in age_group_labels.items():
    hex_gdf[age_group] = hex_gdf[age_group].astype(float)

    # Create interactive hexagonal map
    fig = px.choropleth_mapbox(
        hex_gdf, geojson=hex_gdf.geometry, 
        locations=hex_gdf.index, color=age_group,
        hover_name="Voivodship", 
        mapbox_style="white-bg", 
        zoom=5, center={"lat": 52.069167, "lon": 19.480556},
        opacity=0.9, 
        labels={age_group: label},
        hover_data={'Voivodship': True, 'h3_index': False},
        color_continuous_scale=colorscale  
    )
    fig.update_traces(marker_line=dict(width=3, color='white'))  # Add white lines between hexagons
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
    cmap = mcolors.LinearSegmentedColormap.from_list("mycmap", colorscale)  # Create color map


    # Add legend with color dots
    min_val = hex_gdf[age_group].min()
    max_val = hex_gdf[age_group].max()
    for i in np.linspace(min_val, max_val, 5):
        normalized_i = (i - min_val) / (max_val - min_val)  # Normalize to 0-1 range
        color = cmap(normalized_i)  # Interpolate color
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=400, color='rgba'+str(color)),  # dot size and color
            legendgroup="Life Expectancy", name=f"{round(i, 2)}",  # Round to 2 decimal places
            showlegend=True
        ))
    # Save to HTML file
    fig.write_html(f"{output_dir}/{label}.html")

    print(f"Interactive map has been saved in the directory: {output_dir}/{label}.html")
