import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import h3
from shapely.geometry import Polygon
import os
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import argparse

# Create argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--file_path', type=str, help='Path to the Excel file')
parser.add_argument('--shapefile_path', type=str, help='Path to the shapefile')
parser.add_argument('--output_dir', type=str, help='Output directory for hex maps')
args = parser.parse_args()
df = pd.read_excel(args.file_path)
shapefile_path = args.shapefile_path
gdf = gpd.read_file(shapefile_path)
output_dir = args.output_dir



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

# Change column names to more readable ones
colors = ["#dad66f", "darkgreen"]
# Create a custom color map
cmap = LinearSegmentedColormap.from_list("mycmap", colors)

# Display unique values in the 'Voivodship' column in demographic data
print("Voivodship values in demographic data:")
print(df_combined['Voivodship'].unique())




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

# Generate and save graphic files

for age_group, label in age_group_labels.items():
    vmin = df_combined[age_group].min()
    vmax = df_combined[age_group].max()
    
    fig, ax = plt.subplots(1, 1, figsize=(20, 20)) 
    hex_gdf.boundary.plot(ax=ax, linewidth=2, color='white', alpha=0.0)
    hex_gdf.plot(column=age_group, cmap=cmap, linewidth=2.0, ax=ax, edgecolor='#FFFFFF', legend=False)

    # Adjust axis proportions
    ax.set_aspect('equal', 'box')

    # Set X and Y axis ranges
    ax.set_xlim([hex_gdf.bounds.minx.min(), hex_gdf.bounds.maxx.max()])
    ax.set_ylim([hex_gdf.bounds.miny.min(), hex_gdf.bounds.maxy.max()])
    # Set Y axis range
    y_min = hex_gdf.bounds.miny.min()
    y_max = hex_gdf.bounds.maxy.max()
    y_range = y_max - y_min
    ax.set_ylim([y_min - 0.1 * y_range, y_max + 0.01 * y_range])
    # Add legend with dots
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.5)

    legend_labels = np.linspace(vmin, vmax, num=10)
    for value in legend_labels:
        cax.scatter([], [], color=sm.to_rgba(value), label=f"{value:.2f}", s=2400)  # Increase dot size

    # Position legend so that dots do not overlap, and title does not overlap with legend
    cax.legend(frameon=False, loc='center left', fontsize='15', labelspacing=2, borderpad=2, handletextpad=2, borderaxespad=2, handlelength=0, bbox_to_anchor=(-1., 0.5))
    cax.axis('off')
    # Add title:
    fig.suptitle(label, x=0.5, y=0.95, fontsize=20)
    # Adjust axis proportions
    ax.set_aspect('auto')

    ax.axis('off')
    plt.savefig(f"{output_dir}/{label}.png")
    plt.close(fig)

    print(f"Map has been saved in the directory: {output_dir}/{label}.png")
