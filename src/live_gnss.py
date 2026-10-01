import serial
import csv
from datetime import datetime

#GNSS receiver configuration

# macOS serial port created by the USB-to-UART interface
# on the GNSS receiver board
PORT = "/dev/cu.usbserial-10"

#default serial communication rate used by the LC29H receiver
BAUD_RATE = 115200

CSV_FILE = "data/live_gnss.csv"

# create CSV data log
csv_file = open(CSV_FILE, "w", newline="")
writer = csv.writer(csv_file)

#every row represents one position solution reported by receiver
writer.writerow([
    "timestamp",
    "latitude",
    "longitude",
    "altitude_m",
    "satellites",
    "hdop",
    "fix_quality"
])

#coordinate conversion
def nmea_to_decimal(value, direction):
    """Convert NMEA latitude/longitude to decimal degrees."""

    #latitude uses two digits for degrees (DDMM.MMMM)
    # longitude uses three (DDDMM.MMMM)
    if direction in ("N", "S"):
        degrees = int(value[:2])
        minutes = float(value[2:])
    else:
        degrees = int(value[:3])
        minutes = float(value[3:])

    #convert mins into a fraction of a degree
    decimal = degrees + minutes / 60

    # south and west coordinates are negative (conventional decimal-degree system)
    if direction in ("S", "W"):
        decimal = -decimal

    return decimal

#connect to the physical GNSS receiver
print("Connecting to GNSS receiver...")

try:
    with serial.Serial(PORT, BAUD_RATE, timeout=1) as receiver:

        print("Connected!")
        print("Waiting for GNSS fix...\n")

        while True:
             # read one NMEA message transmitted by the receiver
            line = receiver.readline().decode(
                "ascii", errors="ignore"
            ).strip()

            #only process GGA position messages
            if line.startswith("$GNGGA"):

                fields = line.split(",")

                # make sure position data exists
                if fields[2] and fields[4]:

                    latitude = nmea_to_decimal(
                        fields[2], fields[3]
                    )

                    longitude = nmea_to_decimal(
                        fields[4], fields[5]
                    )

                    #extract GNSS solution information from the GGA message
                    fix_quality = fields[6]
                    satellites = fields[7]
                    hdop = fields[8]
                    altitude = fields[9]

                    timestamp = datetime.now().isoformat(timespec="seconds")

                    writer.writerow([
                    timestamp,
                    latitude,
                    longitude,
                    altitude,
                    satellites,
                    hdop,
                    fix_quality
                    ])
                    # Write immediately so measurements are not held
                    csv_file.flush()

                    # display the GNSS solution in terminal.
                    print("\nLIVE GNSS FIX")
                    print("-------------------------")
                    print(f"Latitude:     {latitude:.6f}°")
                    print(f"Longitude:    {longitude:.6f}°")
                    print(f"Altitude:     {altitude} m")
                    print(f"Satellites:   {satellites}")
                    print(f"HDOP:         {hdop}")
                    print(f"Fix quality:  {fix_quality}")

# Ctrl+C stops
except KeyboardInterrupt:
    print("\nGNSS monitoring stopped.")