import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#load the stationary GNSS measurements 
CSV_FILE = "data/stationary_5min.csv"

data = pd.read_csv(CSV_FILE)

print("GNSS DATASET")
print("-------------------------")
print(data.head())

print("\nNumber of fixes:", len(data))


#mean measured position
mean_lat = data["latitude"].mean()
mean_lon = data["longitude"].mean()

#convert latitude/longitude differences to metres
lat_to_m = 111_320
lon_to_m = 111_320 * np.cos(np.radians(mean_lat))

data["north_error_m"] = (
    data["latitude"] - mean_lat
) * lat_to_m

data["east_error_m"] = (
    data["longitude"] - mean_lon
) * lon_to_m

#horizontal distance from the mean position
data["horizontal_error_m"] = np.sqrt(
    data["north_error_m"] ** 2
    + data["east_error_m"] ** 2
)

#print basic position statistics to the terminal
print("\nPOSITION ANALYSIS")
print("-------------------------")
print(f"Mean latitude:  {mean_lat:.8f}°")
print(f"Mean longitude: {mean_lon:.8f}°")
print(
    f"Mean horizontal error: "
    f"{data['horizontal_error_m'].mean():.3f} m"
)
print(
    f"Maximum horizontal error: "
    f"{data['horizontal_error_m'].max():.3f} m"
)
print(
    f"Position std deviation: "
    f"{data['horizontal_error_m'].std():.3f} m"
)

#radius of 95% of the position measurements
r95 = np.percentile(
    data["horizontal_error_m"],
    95
)

print(f"95th percentile horizontal scatter: {r95:.3f} m")

#plot the spread of the GNSS position measurements in a scatter plot
plt.figure(figsize=(7, 7))

plt.scatter(
    data["east_error_m"],
    data["north_error_m"],
    color="#023382",
    alpha=0.7
)

plt.scatter(
    0,
    0,
    color="#c700a2",
    marker="x",
    s=100,
    label="Mean position"
)

plt.xlabel("East offset from mean (m)")
plt.ylabel("North offset from mean (m)")
plt.title("Stationary GNSS Position Scatter")

plt.axis("equal")
plt.grid(True)
plt.legend()

plt.savefig(
    "figures/live_gnss_scatter.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


#convert timestamps to datetime
data["timestamp"] = pd.to_datetime(data["timestamp"])

# time since recording started
data["elapsed_seconds"] = (
    data["timestamp"] - data["timestamp"].iloc[0]
).dt.total_seconds()

# Plot position drift over time
plt.figure(figsize=(9, 5))

plt.plot(
    data["elapsed_seconds"],
    data["east_error_m"],
    color="#023382",
    label="East offset"
)

plt.plot(
    data["elapsed_seconds"],
    data["north_error_m"],
    color="#ca006c",
    label="North offset"
)

plt.axhline(0, color="#023382",linestyle="--", linewidth=1)

plt.xlabel("Time (seconds)")
plt.ylabel("Offset from mean position (m)")
plt.title("GNSS Position Drift Over Time")

plt.grid(True)
plt.legend()

plt.savefig(
    "figures/live_gnss_drift.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

#plot the number of satellites used and HDOP over time
plt.figure(figsize=(9, 5))

plt.plot(
    data["elapsed_seconds"],
    data["satellites"],
    color="#023382",
    label="Satellites"
)

plt.xlabel("Time (seconds)")
plt.ylabel("Number of satellites")
plt.title("Satellites Used Over Time")

plt.grid(True)
plt.legend()

plt.savefig(
    "figures/satellites_over_time.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

#plot satellite geometry quality (HDOP) over time
plt.figure(figsize=(9, 5))

plt.plot(
    data["elapsed_seconds"],
    data["hdop"],
    color="#023382",
)

plt.xlabel("Time (seconds)")
plt.ylabel("HDOP")
plt.title("GNSS HDOP Over Time")

plt.grid(True)

plt.savefig(
    "figures/hdop_over_time.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

#plot altitude over time
plt.figure(figsize=(9, 5))

plt.plot(
    data["elapsed_seconds"],
    data["altitude_m"],
    color="#023382"
)

plt.xlabel("Time (seconds)")
plt.ylabel("Altitude (m)")
plt.title("GNSS Altitude Over Time")

plt.grid(True)

plt.savefig(
    "figures/altitude_over_time.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

#plot horizontal position stability over time
plt.figure(figsize=(9, 5))

plt.plot(
    data["elapsed_seconds"],
    data["horizontal_error_m"],
    color="#002d76",
)

plt.xlabel("Time (seconds)")
plt.ylabel("Horizontal displacement from mean (m)")
plt.title("GNSS Horizontal Position Stability Over Time")

plt.grid(True)

plt.savefig(
    "figures/horizontal_stability.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
