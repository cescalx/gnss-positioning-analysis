import numpy as np 

def ecef_to_geodetic(x, y, z):
    """
    Convert ECEF coordinates to WGS84
    latitude, longitude and altitude.
    """

    # WGS84 ellipsoid constants
    a = 6378137.0
    f = 1 / 298.257223563

    e2 = f * (2 - f)

    # Longitude
    lon = np.arctan2(y, x)

    # Initial latitude estimate
    p = np.sqrt(x**2 + y**2)
    lat = np.arctan2(z, p * (1 - e2))

    # Iteratively improve latitude
    for _ in range(10):
        N = a / np.sqrt(1 - e2 * np.sin(lat)**2)

        altitude = p / np.cos(lat) - N

        lat_new = np.arctan2(
            z,
            p * (1 - e2 * N / (N + altitude))
        )

        if abs(lat_new - lat) < 1e-12:
            lat = lat_new
            break

        lat = lat_new

    # Final altitude
    N = a / np.sqrt(1 - e2 * np.sin(lat)**2)
    altitude = p / np.cos(lat) - N

    return (
        np.degrees(lat),
        np.degrees(lon),
        altitude
    )