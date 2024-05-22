import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Wczytanie danych z pliku Excel
file_path = 'table_b_life_expectancy_in_poland_by_voivodships_in_2022.xlsx'
df = pd.read_excel(file_path)

# Usuwamy pierwsząkolumnę
df = df.iloc[:, 1:]

# Wybieramy tylko wiersze od 0 do 21 (22 wiersze łącznie) 
df_total = df.iloc[5:22, :]




# Zakładamy, że kolumny 3, 4, 5, 6 zawierają dane o mężczyznach
df_men = df_total.iloc[:, [0, 1, 2, 3, 4, 5]]
# Zmieniamy nazwy kolumn dla mężczyzn
df_men.columns = ['Voivodship', 'Male_0' , 'Male_15' , 'Male_30', 'Male_45', 'Male_60']


# Zakładamy, że kolumny 6, 7, 8, 9, 10 zawierają dane o kobietach
df_women = df_total.iloc[:, [0, 6, 7, 8, 9, 10]]
# Zmieniamy nazwy kolumn dla kobiet
df_women.columns = ['Voivodship', 'Female_0' , 'Female_15' , 'Female_30', 'Female_45', 'Female_60']





# Sprawdzenie pierwszych 100 rekordów dla mężczyzn
print(df_men.head(100))
# Sprawdzenie pierwszych 100 rekordów dla kobiet
print(df_women.head(100))



# Zapisanie danych do pliku Excel
output_file = 'output_data.xlsx'
with pd.ExcelWriter(output_file) as writer:
    df_men.to_excel(writer, sheet_name='Men', index=False)
    df_women.to_excel(writer, sheet_name='Women', index=False)





