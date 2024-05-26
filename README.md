### README.md

# Hexagonal Life Expectancy Maps for Poland

This project generates hexagonal maps to visualize life expectancy in Poland based on demographic data. The project utilizes various libraries including `pandas`, `geopandas`, `plotly`, `h3-py`, and `matplotlib` to create interactive and static visualizations.

## Table of Contents
- [Usage](#usage)
- [Arguments](#arguments)
- [Example](#example)
- [Output](#output)
- [Data Source](#data-source)


## Usage

### For Static Maps
To generate static hexagonal maps, run the following command:
```bash
python create_hex_map.py --shapefile_path path/to/shapefile.shp --output_dir path/to/output --file_path path/to/datafile.xlsx
```

### For Interactive Maps
To generate interactive hexagonal maps, run the following command:
```bash
python create_hex_map_interactive.py --shapefile_path path/to/shapefile.shp --output_dir path/to/output --file_path path/to/datafile.xlsx
```

## Arguments

- `--shapefile_path`: Path to the shapefile containing the administrative boundaries of Poland.
- `--output_dir`: Directory where the generated maps will be saved.
- `--file_path`: Path to the Excel file containing the demographic data.

## Example

### For Static Maps
```bash
python create_hex_map.py --shapefile_path "Shape Files/A01_Granice_wojewodztw.shp" --output_dir "hex_maps" --file_path "table_b_life_expectancy_in_poland_by_voivodships_in_2022.xlsx"
```

### For Interactive Maps
```bash
python create_hex_map_interactive.py --shapefile_path "Shape Files/A01_Granice_wojewodztw.shp" --output_dir "hex_maps_interactive" --file_path "table_b_life_expectancy_in_poland_by_voivodships_in_2022.xlsx"
```

## Output

The scripts generate both interactive and static maps for different age groups and genders. The maps will be saved in the specified output directories.

### Interactive Maps

Interactive maps are saved as HTML files, which can be opened in any web browser.

### Static Maps

Static maps are saved as PNG files.

## Data Source

The demographic data used in this project is sourced from the [Life Expectancy Tables of Poland 2022](https://stat.gov.pl/en/topics/population/life-expectancy/life-expectancy-tables-of-poland-2022,2,16.html) published by Statistics Poland.

