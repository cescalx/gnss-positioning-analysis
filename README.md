# GNSS Positioning Analysis

A Python-based GNSS positioning pipeline that processes RINEX observation and navigation data to estimate a receiver's position from satellite pseudorange measurements.

The project implements the core stages of standalone GNSS positioning, including broadcast ephemeris processing, satellite position calculation, satellite clock correction, Earth-rotation correction, iterative least-squares positioning, and pseudorange residual analysis.

## Project Pipeline

```text
RINEX Observation + Navigation Data
                ↓
        Pseudorange Extraction
                ↓
       Broadcast Ephemerides
                ↓
     Satellite ECEF Positions
                ↓
      Satellite Clock Correction
                ↓
   Earth-Rotation / Sagnac Correction
                ↓
    Iterative Least-Squares Solution
                ↓
     Receiver ECEF Coordinates
                ↓
 Latitude / Longitude / Altitude
                ↓
      Residual Performance Analysis
```

## Results

For the sample GNSS epoch analysed, the positioning solution used multiple GPS satellites and produced:

- **Pseudorange residual RMSE:** 6.66 m
- **Maximum absolute residual:** 11.47 m
- **Estimated receiver altitude:** 516.27 m
- **Receiver clock bias:** 30.12 m

The residuals were evaluated across the satellites used in the least-squares position solution.

![GNSS Pseudorange Residuals](figures/pseudorange_residuals.png)

## How It Works

### 1. RINEX Data Processing

The pipeline reads RINEX observation and navigation files using GeoRinex. The observation file provides GPS pseudorange measurements, while the navigation file provides the broadcast ephemeris parameters required to calculate satellite positions.

### 2. Satellite Position Calculation

For each usable GPS satellite, the broadcast orbital parameters are used to calculate its position in Earth-Centred Earth-Fixed (ECEF) coordinates at the estimated signal transmission time.

The signal travel time is approximated using:

τ = ρ / c

where `ρ` is the measured pseudorange and `c` is the speed of light.

### 3. GNSS Corrections

Two important corrections are applied before solving for the receiver position:

- **Satellite clock correction** — compensates for offsets in the satellite's onboard clock using the broadcast clock parameters.
- **Earth-rotation (Sagnac) correction** — accounts for the rotation of the Earth while the GNSS signal travels from the satellite to the receiver.

### 4. Receiver Position Solution

The corrected pseudoranges and satellite ECEF coordinates are used in an iterative nonlinear least-squares solution.

For each satellite:

ρᵢ ≈ √[(xᵢ − x)² + (yᵢ − y)² + (zᵢ − z)²] + b

where `(x, y, z)` is the unknown receiver position and `b` is the receiver clock bias.

The resulting ECEF position is then converted into latitude, longitude and altitude.

### 5. Residual Analysis

After solving for the receiver position, predicted pseudoranges are compared with the observed pseudoranges.

The residuals provide a measure of how well the final position solution explains the GNSS observations. For the analysed epoch, the solution achieved an RMSE of **6.66 m**.

## Project Structure

## Project Structure

The project is organised into the following main directories:

- `data/` — RINEX observation and navigation data
- `figures/` — generated GNSS analysis figures
- `notebooks/` — exploratory analysis
- `src/` — Python source code for the positioning pipeline

Key source files include:

- `read_rinex.py` — main GNSS positioning pipeline
- `satellite_position.py` — satellite ECEF position calculation
- `positioning.py` — iterative least-squares receiver positioning
- `coordinates.py` — ECEF to geodetic coordinate conversion
- `read_navigation.py` — navigation data processing

## Technologies

- Python
- NumPy
- Matplotlib
- GeoRinex
- xarray
- RINEX GNSS data

## Key Skills Demonstrated

- Scientific Python programming
- GNSS data processing
- Numerical modelling
- Coordinate transformations
- Nonlinear least-squares estimation
- Satellite orbit calculations
- Measurement correction and residual analysis
- Data visualisation
- Working with real scientific datasets

## Running the Project

Clone the repository and create a Python virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install the required dependencies:

    pip install numpy matplotlib georinex xarray

Run the positioning pipeline from the project root:

    python src/read_rinex.py

The program reads the RINEX observation and navigation data, calculates satellite positions, applies GNSS corrections, solves for the receiver position, evaluates pseudorange residuals, and saves the residual plot to the `figures/` directory.

## Future Improvements

Possible extensions to the positioning pipeline include:

- Processing multiple observation epochs to analyse positioning performance over time
- Comparing the calculated solution against a known reference receiver position
- Adding ionospheric and tropospheric delay corrections
- Supporting addition## Running the Project

Clone the repository and create a Python virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install the required dependencies:

    pip install numpy matplotlib georinex xarray

Run the positioning pipeline from the project root:

    python src/read_rinex.py

The program reads the RINEX observation and navigation data, calculates satellite positions, applies GNSS corrections, solves for the receiver position, evaluates pseudorange residuals, and saves the residual plot to the `figures/` directory.

## Future Improvements

Possible extensions to the positioning pipeline include:

- Processing multiple observation epochs to analyse positioning performance over time
- Comparing the calculated solution against a known reference receiver position
- Adding ionospheric and tropospheric delay corrections
- Supporting additional GNSS constellations such as Galileo
- Analysing satellite geometry and dilution of precision (DOP)

## Summary

This project demonstrates the development of a standalone GNSS positioning pipeline from raw RINEX measurements to a corrected receiver position solution.

It combines satellite orbital modelling, GNSS measurement corrections, coordinate transformations, nonlinear least-squares estimation, residual analysis and data visualisation within a reproducible Python workflow.al GNSS constellations such as Galileo
- Analysing satellite geometry and dilution of precision (DOP)

## Summary

This project demonstrates the development of a standalone GNSS positioning pipeline from raw RINEX measurements to a corrected receiver position solution.

It combines satellite orbital modelling, GNSS measurement corrections, coordinate transformations, nonlinear least-squares estimation, residual analysis and data visualisation within a reproducible Python workflow.