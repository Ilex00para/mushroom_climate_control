from machine import Pin, SoftI2C
from time import sleep
from micropython import const

humidifierPin = Pin(5, Pin.OUT)

class SCD4_sensor:
    # Class variables
    SENSOR_ADDRESS = 0x62
    START_PERIODIC_MEASUREMENT = const(0x21AC) #Low Power Measurements every 30 seconds
    GET_DATA_READY_STATUS = const(0xE4B8)
    READ_MEASUREMENT = const(0xEC05)
    STOP_PERIODIC_MEASUREMENT = const(0x3F86)


    def __init__(self, sda, scl, address=SENSOR_ADDRESS) -> None:
        self.i2c = SoftI2C(sda=Pin(sda), scl=Pin(scl))
        self.address = address
        self._cmd = bytearray(2)
        self._crc_buffer = bytearray(2)
        self._buffer = bytearray(18)

        self._co2 = None
        self._temperature = None
        self._relative_humidity = None
        
        # Check if the sensor is connected
        if self.address in self.i2c.scan():
            print(f"Found sensor at address {hex(self.address)}")
        else:
            print(f"Sensor not found at address {hex(self.address)}")
        # Consider handling this case (e.g., exit or retry)
        self.i2c.writeto(self.address, self.STOP_PERIODIC_MEASUREMENT.to_bytes(2, 'big'))
        sleep(1)
        self.i2c.writeto(self.address, self.START_PERIODIC_MEASUREMENT.to_bytes(2, 'big'))
        sleep(0.005)
        

    def _read_data(self):
        """Reads the temp/hum/co2 from the sensor and caches it"""
        self._send_command(self.READ_MEASUREMENT, cmd_delay=0.001)
        self._read_reply(self._buffer, 9)

        self._co2 = (self._buffer[0] << 8) | self._buffer[1]

        temperature = (self._buffer[3] << 8) | self._buffer[4]
        self._temperature = -45 + 175 * (temperature / 2 ** 16)

        humi = (self._buffer[6] << 8) | self._buffer[7]
        self._relative_humidity = 100 * (humi / 2 ** 16)

        print(f"CO2: {self._co2} ppm, Temperature: {self._temperature:.2f} °C, Humidity: {self._relative_humidity:.2f} %")

    @property
    def data_ready(self):
        """Check the sensor to see if new data is available"""
        self._send_command(self.GET_DATA_READY_STATUS, cmd_delay=0.001)
        self._read_reply(self._buffer, 3)
        return not ((self._buffer[0] & 0x03 == 0) and (self._buffer[1] == 0))

    def stop_periodic_measurement(self):
        """Stop measurement mode"""
        self._send_command(self.STOP_PERIODIC_MEASUREMENT, cmd_delay=0.5)

    def start_periodic_measurement(self):
        """Put sensor into working mode, about 5s per measurement"""
        self._send_command(self.START_PERIODIC_MEASUREMENT, cmd_delay=0.01)

    def _send_command(self, cmd, cmd_delay=0.0):
        self._cmd[0] = (cmd >> 8) & 0xFF
        self._cmd[1] = cmd & 0xFF
        self.i2c.writeto(self.address, self._cmd)
        sleep(cmd_delay)

    def _read_reply(self, buff, num):
        self.i2c.readfrom_into(self.address, buff, num)
        self._check_buffer_crc(self._buffer[0:num])

    def _check_buffer_crc(self, buf):
        for i in range(0, len(buf), 3):
            self._crc_buffer[0] = buf[i]
            self._crc_buffer[1] = buf[i + 1]
            if self._crc8(self._crc_buffer) != buf[i + 2]:
                raise RuntimeError("CRC check failed while reading data")
        return True

    @staticmethod
    def _crc8(buffer):
        crc = 0xFF
        for byte in buffer:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x31
                else:
                    crc = crc << 1
        return crc & 0xFF  # return the bottom 8 bits



if __name__ == "__main__":
    scd4 = SCD4_sensor(sda=4,scl=11)

    while True:
        if scd4.data_ready:
            scd4._read_data()
            if scd4._relative_humidity < 80.0:
              humidifierPin.value(1)
              sleep(2)
              humidifierPin.value(0)
            
        sleep(30)