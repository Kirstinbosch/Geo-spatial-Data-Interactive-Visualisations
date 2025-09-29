import pandas as pd

# Load the CSV
df = pd.read_csv("fires-all 2.csv", sep=";", skiprows=1)

# Convert Date column
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Filter for years 2013–2023
df = df[(df['Date'].dt.year >= 2013) & (df['Date'].dt.year <= 2023)]

# Count rows (fires)
fire_count = len(df)

print(f"Total number of fires between 2013 and 2023: {fire_count}")

import pandas as pd

# Load the CSV
df = pd.read_csv("fires-all 2.csv", sep=";", skiprows=1)

# Convert Date column
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Filter for years 2013–2023
df = df[(df['Date'].dt.year >= 2013) & (df['Date'].dt.year <= 2023)]

# Ensure superficie is numeric
df['superficie'] = pd.to_numeric(df['superficie'], errors='coerce')

# Count fires
fire_count = len(df)

# Total burned area
total_burned = df['superficie'].sum()

print(f"Total number of fires between 2013 and 2023: {fire_count}")
print(f"Total burned area between 2013 and 2023: {total_burned:,.0f} hectares")

# Compare with some known land areas (all in hectares)
land_areas = {
    "Mallorca (Balearic Islands)": 364000,  # ha
    "Rhode Island (USA)": 314000,           # ha
    "Luxembourg": 258600,                   # ha
    "Greater London": 157200                # ha
}

for name, area in land_areas.items():
    ratio = total_burned / area
    print(f"≈ {ratio:.2f} times the size of {name}")



