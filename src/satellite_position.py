import numpy as np

# physical constants
MU = 3.986005e14          # Earth's gravitational constant [m^3/s^2]
OMEGA_E = 7.2921151467e-5 # Earth's rotation rate [rad/s]


def solve_kepler(mean_anomaly, eccentricity, tolerance=1e-12):
    """
    solve Kepler's equation:
        M = E - e sin(E)

    Returns the eccentric anomaly E.
    """

    E = mean_anomaly

    for _ in range(100):
        E_new = mean_anomaly + eccentricity * np.sin(E)

        if abs(E_new - E) < tolerance:
            return E_new

        E = E_new

    return E


# orbital parameters into a satellite position in ECEF coordinates.
def satellite_position(ephemeris, transmit_time):
    """
    Calculate GPS satellite ECEF position from broadcast ephemeris.

    Parameters
    ----------
    ephemeris : xarray Dataset/DataArray
        Broadcast ephemeris for one satellite.
    transmit_time : float
        Time since GPS week start in seconds.

    Returns
    -------
    np.ndarray
        Satellite ECEF position [x, y, z] in metres.
    """

    sqrtA = float(ephemeris["sqrtA"])
    A = sqrtA ** 2

    e = float(ephemeris["Eccentricity"])
    M0 = float(ephemeris["M0"])
    delta_n = float(ephemeris["DeltaN"])
    toe = float(ephemeris["Toe"])

    omega = float(ephemeris["omega"])
    omega0 = float(ephemeris["Omega0"])
    omega_dot = float(ephemeris["OmegaDot"])

    i0 = float(ephemeris["Io"])
    idot = float(ephemeris["IDOT"])

    cuc = float(ephemeris["Cuc"])
    cus = float(ephemeris["Cus"])
    crc = float(ephemeris["Crc"])
    crs = float(ephemeris["Crs"])
    cic = float(ephemeris["Cic"])
    cis = float(ephemeris["Cis"])

    # time from ephemeris reference epoch
    tk = transmit_time - toe

    # correct for GPS week crossover
    if tk > 302400:
        tk -= 604800
    elif tk < -302400:
        tk += 604800

    # computed mean motion
    n0 = np.sqrt(MU / A**3)
    n = n0 + delta_n

    # mean anomaly
    M = M0 + n * tk

    # solve Kepler equation
    E = solve_kepler(M, e)

    # true anomaly
    v = np.arctan2(
        np.sqrt(1 - e**2) * np.sin(E),
        np.cos(E) - e
    )

    # argument of latitude
    phi = v + omega

    # Harmonic corrections
    du = cuc * np.cos(2 * phi) + cus * np.sin(2 * phi)
    dr = crc * np.cos(2 * phi) + crs * np.sin(2 * phi)
    di = cic * np.cos(2 * phi) + cis * np.sin(2 * phi)

    # corrected values
    u = phi + du
    r = A * (1 - e * np.cos(E)) + dr
    i = i0 + di + idot * tk

    # orbital plane coordinates
    x_orb = r * np.cos(u)
    y_orb = r * np.sin(u)

    # corrected longitude of ascending node
    omega_k = (
        omega0
        + (omega_dot - OMEGA_E) * tk
        - OMEGA_E * toe
    )

    # convert to Earth-centred Earth-fixed coordinates
    x = x_orb * np.cos(omega_k) - y_orb * np.cos(i) * np.sin(omega_k)
    y = x_orb * np.sin(omega_k) + y_orb * np.cos(i) * np.cos(omega_k)
    z = y_orb * np.sin(i)

    return np.array([x, y, z])

def earth_rotation_correction(position, travel_time):
    """
    Correct satellite ECEF coordinates for Earth rotation
    during signal travel time.
    """

    angle = OMEGA_E * travel_time

    rotation = np.array([
        [np.cos(angle),  np.sin(angle), 0.0],
        [-np.sin(angle), np.cos(angle), 0.0],
        [0.0,            0.0,           1.0]
    ])

    return rotation @ position