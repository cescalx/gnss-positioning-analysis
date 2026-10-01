import georinex as gr
import numpy as np
import matplotlib.pyplot as plt

from satellite_position import (
    satellite_position,
    earth_rotation_correction
)
from positioning import solve_receiver_position
from coordinates import ecef_to_geodetic


C = 299792458.0  # speed of light in m/s

def gps_seconds_of_week(datetime64):
    """Convert a NumPy datetime64 timestamp to GPS seconds-of-week."""

    gps_epoch = np.datetime64("1980-01-06T00:00:00")

    seconds_since_gps_epoch = (
        datetime64 - gps_epoch
    ) / np.timedelta64(1, "s")

    gps_week = int(seconds_since_gps_epoch // (7 * 24 * 3600))

    seconds_of_week = (
        seconds_since_gps_epoch
        - gps_week * 7 * 24 * 3600
    )

    return float(seconds_of_week)

# load first RINEX observation file
obs = gr.load("data/real/observations.16o")
nav = gr.load("data/real/navigation.16n")

print("RINEX file loaded successfully!")
print()
print(obs)


print("\nSatellites observed:")
print(obs.sv.values)

print("\nC1 pseudorange measurements:")

for satellite in obs.sv.values:
    pseudorange = obs["C1"].sel(sv=satellite).values[0]

    if not np.isnan(pseudorange):
        print(f"{satellite}: {pseudorange:,.2f} metres")


# test satellite position calculation for one satellite
test_satellite = "G01"  # eg satellite, change as needed

records = nav.sel(sv=test_satellite).dropna(dim="time", how="all")

# use the first ephemeris record for now
ephem = records.isel(time=0)

# GPS seconds of week for first observation epoch
transmit_time = float(ephem["Toe"])

position = satellite_position(ephem, transmit_time)

print(f"\nApproximate ECEF position for {test_satellite}:")
print(f"X = {position[0]:,.2f} m")
print(f"Y = {position[1]:,.2f} m")
print(f"Z = {position[2]:,.2f} m")

print(f"\nDistance from Earth's centre:")
print(f"{np.linalg.norm(position):,.2f} m")

# get G01 pseudorange at the first observation epoch
epoch = obs.time.values[0]
receive_time = gps_seconds_of_week(epoch)

print("\nObservation time:")
print(epoch)

print("\nGPS seconds-of-week:")
print(f"{receive_time:.3f} s")
first_epoch = obs.sel(time=epoch)

pseudorange = float(first_epoch["C1"].sel(sv="G01").values)

# estimate signal travel time
travel_time = pseudorange / C

# use ephemeris Toe as our GPS-time reference for this simple test
test_receive_time = float(ephem["Toe"])
test_transmit_time = test_receive_time - travel_time

print("\nSignal travel time:")
print(f"{travel_time:.6f} seconds")

print("\nEstimated transmit time:")
print(f"{test_transmit_time:.6f} seconds")

# recalculate satellite position at transmit time
position_tx = satellite_position(ephem, test_transmit_time)

print("\nECEF position at estimated transmit time:")
print(f"X = {position_tx[0]:,.2f} m")
print(f"Y = {position_tx[1]:,.2f} m")
print(f"Z = {position_tx[2]:,.2f} m")

#  find GPS satellites with valid pseudorange measurements
valid_satellites = []

for satellite in obs.sv.values:
    satellite = str(satellite)

    if satellite.startswith("G"):
        pseudorange = first_epoch["C1"].sel(sv=satellite).values

        if not np.isnan(pseudorange) and satellite in nav.sv.values:
            valid_satellites.append(satellite)

print("\nUsable GPS satellites:")
print(valid_satellites)
print(f"Number of usable satellites: {len(valid_satellites)}")

satellite_data = []

for satellite in valid_satellites:
    pseudorange = float(first_epoch["C1"].sel(sv=satellite).values)

    records = nav.sel(sv=satellite).dropna(dim="time", how="all")

    # choose the ephemeris closest to but not after the observation epoch
    valid_times = records.time.values[
        records.time.values <= epoch
    ]

    if len(valid_times) == 0:
        print(f"{satellite}: no suitable ephemeris")
        continue

    ephem_time = valid_times[-1]
    ephem = records.sel(time=ephem_time)

    # estimate signal travel time
    travel_time = pseudorange / C
    transmit_time = receive_time - travel_time

    # satellite clock correction
    af0 = float(ephem["SVclockBias"])
    af1 = float(ephem["SVclockDrift"])
    af2 = float(ephem["SVclockDriftRate"])

    toc = gps_seconds_of_week(ephem.time.values)

    dt = transmit_time - toc

    # GPS week crossover correction
    if dt > 302400:
        dt -= 604800
    elif dt < -302400:
        dt += 604800

    sat_clock = (
        af0
        + af1 * dt
        + af2 * dt**2
    )

    # correct the pseudorange
    corrected_pseudorange = pseudorange + C * sat_clock

    # recalculate signal travel time
    travel_time = corrected_pseudorange / C
    transmit_time = receive_time - travel_time

    # calculate satellite ECEF position
    position = satellite_position(
        ephem,
        transmit_time
    )
    position = earth_rotation_correction(
        position,
          travel_time
    )

    # store corrected pseudorange + satellite position
    satellite_data.append([
        satellite,
        corrected_pseudorange,
        position[0],
        position[1],
        position[2]
    ])


print("\nSatellite positioning inputs:")

for row in satellite_data:
    satellite, pseudorange, x, y, z = row

    print(
        f"{satellite} | "
        f"rho = {pseudorange:,.2f} m | "
        f"X = {x:,.2f} | "
        f"Y = {y:,.2f} | "
        f"Z = {z:,.2f}"
    )

# convert satellite data into arrays for positioning
satellite_positions = np.array([
    [row[2], row[3], row[4]]
    for row in satellite_data
])

pseudoranges = np.array([
    row[1]
    for row in satellite_data
])

# solve for receiver position
receiver_state, residuals = solve_receiver_position(
    satellite_positions,
    pseudoranges
)

x, y, z, clock_bias = receiver_state

print("\nEstimated receiver ECEF position:")
print(f"X = {x:,.2f} m")
print(f"Y = {y:,.2f} m")
print(f"Z = {z:,.2f} m")

print("\nReceiver clock bias:")
print(f"{clock_bias:,.2f} m")

print("\nDistance from Earth's centre:")
print(f"{np.linalg.norm([x, y, z]):,.2f} m")

# convert receiver ECEF position to latitude, longitude and altitude
latitude, longitude, altitude = ecef_to_geodetic(x, y, z)

print("\nEstimated receiver location:")
print(f"Latitude  = {latitude:.6f}°")
print(f"Longitude = {longitude:.6f}°")
print(f"Altitude  = {altitude:.2f} m")

print("\nPseudorange residuals:")

for satellite, residual in zip(valid_satellites, residuals):
    print(f"{satellite}: {residual:.2f} m")

rmse = np.sqrt(np.mean(residuals**2))

print("\nResidual statistics:")
print(f"Mean residual = {np.mean(residuals):.2f} m")
print(f"RMSE = {rmse:.2f} m")
print(f"Maximum absolute residual = {np.max(np.abs(residuals)):.2f} m")

# plot pseudorange residuals
satellite_names = valid_satellites[:len(residuals)]

plt.figure(figsize=(10, 5))

plt.bar(satellite_names, residuals, color="#002b71", edgecolor='#00122e')

plt.axhline(
    0,
    linewidth=1
)

plt.xlabel("GPS Satellite")
plt.ylabel("Pseudorange Residual (m)")
plt.title("GNSS Pseudorange Residuals")

plt.tight_layout()
plt.savefig("figures/pseudorange_residuals.png", dpi=300)
plt.show()