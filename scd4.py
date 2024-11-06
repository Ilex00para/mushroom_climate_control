from machine import Pin, SoftI2C
from time import sleep
from micropython import const

# Initialize I2C
i2c = SoftI2C(scl=Pin(11), sda=Pin(4))

# Sensor I2C address
sensor_address = 0x62

# Command codes (corrected)
START_MEASUREMENT_CMD = const(0x21B1)
GET_DATA_READY_STATUS = const(0xE4B8)
READ_MEASUREMENT = const(0xEC05)

# Initialize buffers
status_buffer = bytearray(3)    # For reading 3-byte status
data_buffer = bytearray(9)      # For reading 9-byte measurement data

# Check if the sensor is connected
if sensor_address in i2c.scan():
    print(f"Found sensor at address {hex(sensor_address)}")
else:
    print(f"Sensor not found at address {hex(sensor_address)}")
    # Consider handling this case (e.g., exit or retry)

# Start periodic measurement
i2c.writeto(sensor_address, START_MEASUREMENT_CMD.to_bytes(2, 'big'))
sleep(0.005)  # Small delay to ensure command is processed

while True:
    # Send the GET_DATA_READY_STATUS command
    i2c.writeto(sensor_address, GET_DATA_READY_STATUS.to_bytes(2, 'big'))
    sleep(0.001)  # Small delay for sensor to process the command

    # Read the 3-byte status response
    i2c.readfrom_into(sensor_address, status_buffer)
    # Combine the two bytes to form a 16-bit status word
    status_word = (status_buffer[0] << 8) | status_buffer[1]
    # (Optional) Verify the CRC byte status_buffer[2]

    # Check if data is ready (least significant 11 bits not zero)
    if (status_word & 0x07FF) != 0:
        # Data is ready
        # Send the READ_MEASUREMENT command
        i2c.writeto(sensor_address, READ_MEASUREMENT.to_bytes(2, 'big'))
        sleep(0.001)  # Small delay for sensor to process the command

        # Read the 9-byte measurement data
        i2c.readfrom_into(sensor_address, data_buffer)

        # Extract CO2 concentration
        co2_raw = (data_buffer[0] << 8) | data_buffer[1]
        co2_crc = data_buffer[2]  # Optional: verify CRC

        # Extract temperature
        temp_raw = (data_buffer[3] << 8) | data_buffer[4]
        temp_crc = data_buffer[5]  # Optional: verify CRC
        temperature = -45 + 175 * (temp_raw / 65536)

        # Extract humidity
        hum_raw = (data_buffer[6] << 8) | data_buffer[7]
        hum_crc = data_buffer[8]  # Optional: verify CRC
        humidity = 100 * (hum_raw / 65536)

        # Print the results
        print(f"CO2: {co2_raw} ppm, Temperature: {temperature:.2f} °C, Humidity: {humidity:.2f} %")
    else:
        print("Data not ready")

    sleep(4)  # Wait before checking again
