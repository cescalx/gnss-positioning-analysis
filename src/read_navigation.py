import georinex as gr
import numpy as np

# Load real RINEX files
obs = gr.load("data/real/observations.16o")
nav = gr.load("data/real/navigation.16n")

print("Observation file loaded successfully!")
print("Navigation file loaded successfully!")

# GPS satellites only
obs_gps = [sv for sv in obs.sv.values if str(sv).startswith("G")]
nav_gps = [sv for sv in nav.sv.values if str(sv).startswith("G")]

print("\nGPS satellites in observation file:")
print(obs_gps)

print("\nGPS satellites in navigation file:")
print(nav_gps)

# Satellites present in both files
common = sorted(set(obs_gps).intersection(nav_gps))

print("\nMatching GPS satellites:")
print(common)

print("\nNumber of matching GPS satellites:")
print(len(common))

# Select the first observation time
epoch = obs.time.values[0]

print("\nFirst observation time:")
print(epoch)

# Get observations at this time
first_epoch = obs.sel(time=epoch)

# Find the available measurement types
print("\nAvailable observation types:")
print(list(first_epoch.data_vars))

# Find GPS satellites with a valid C1 pseudorange at this epoch
print("\nGPS satellites with valid C1 pseudoranges:")

valid_satellites = []

for satellite in common:
    pseudorange = first_epoch["C1"].sel(sv=satellite).values

    if not np.isnan(pseudorange):
        valid_satellites.append(satellite)
        print(f"{satellite}: {pseudorange:,.2f} metres")

print("\nNumber of usable satellites:")
print(len(valid_satellites))

#checking ephemeris availability for all 11 
print("\nChecking navigation data for usable satellites:")

for satellite in valid_satellites:
    if satellite in nav.sv.values:
        records = nav.sel(sv=satellite)
        valid_records = records.dropna(dim="time", how="all")

        print(f"{satellite}: {valid_records.sizes['time']} ephemeris records")
    else:
        print(f"{satellite}: no navigation data")

#checking one satellite ephemeris 

example_satellite = valid_satellites[0]

records = nav.sel(sv=example_satellite)
valid_records = records.dropna(dim="time", how="all")

print(f"\nExample ephemeris data for {example_satellite}:")
print(valid_records.isel(time=0))