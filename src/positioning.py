import numpy as np


def solve_receiver_position(satellite_positions, pseudoranges):
    """
    Estimate receiver ECEF position and clock bias
    using iterative least squares.
    """

    # Initial estimate: centre of Earth, zero clock bias
    state = np.array([0.0, 0.0, 0.0, 0.0])

    for _ in range(10):

        x, y, z, b = state

        predicted_ranges = np.sqrt(
            (satellite_positions[:, 0] - x) ** 2
            + (satellite_positions[:, 1] - y) ** 2
            + (satellite_positions[:, 2] - z) ** 2
        )

        residuals = pseudoranges - (predicted_ranges + b)

        H = np.zeros((len(satellite_positions), 4))

        H[:, 0] = (x - satellite_positions[:, 0]) / predicted_ranges
        H[:, 1] = (y - satellite_positions[:, 1]) / predicted_ranges
        H[:, 2] = (z - satellite_positions[:, 2]) / predicted_ranges
        H[:, 3] = 1.0

        correction, _, _, _ = np.linalg.lstsq(
            H,
            residuals,
            rcond=None
        )

        state += correction

        if np.linalg.norm(correction[:3]) < 0.001:
            break

    #final residual after convergence
    x, y, z, b = state
    predicted_ranges = np.sqrt(
        (satellite_positions[:, 0] - x) ** 2
        + (satellite_positions[:, 1] - y) ** 2
        + (satellite_positions[:, 2] - z) ** 2
    )
    residuals = pseudoranges - (predicted_ranges + b)
    return state, residuals