from machine import UART
from time import sleep

# Initialize UART (TX=17, RX=16)


class WioE5:
    def __init__(self,baudrate=9600, tx=43, rx=44):
        APPKEY= 'F20A322E41822E47F6C61BAF29666158'
        self.uart = UART(2, baudrate=baudrate, tx=tx, rx=rx)
        # Configure the Wio-E5 for LoRa Communication
        print("Configuring Wio-E5...")
        self.send_at_command("AT")
        self.DevEui = self.send_at_command("AT+ID=DevEui")  # Example LoRaWAN Device Address
        self.AppEui = self.send_at_command("AT+ID=AppEui")
        self.send_at_command(f"AT+KEY=APPKEY,{APPKEY}")  # Application session key
        self.send_at_command("AT+DR=EU868")# Set Data Rate (region-specific)
        self.send_at_command("AT+CH=NUM,0-2")
        self.send_at_command("AT+MODE=LWOTAA")  
        #send_at_command("AT+FREQ=868100000")    # Set frequency (868 MHz for EU)
        self.join_network()
        

    def send_at_command(self,command, delay=0.5):
        """
        Sends an AT command to the Wio-E5 and reads the response.
        """
        self.uart.write(command + '\r\n')  # Send the AT command
        sleep(delay)  # Wait for response
        if self.uart.any():  # Check if data is available
            response = self.uart.read().decode('utf-8')  # Read and decode the response
            print(f"Response: {response}")
            return response
        else:
            print("No response received")
            return ""

    def join_network(self):
        response = '+JOIN: Join failed'
        tries = 0
        while '+JOIN: Join failed' in response and tries < 3:
            self.uart.write('AT+JOIN'+ '\r\n')  # Send the AT command
            sleep(10)  # Wait for response
        
            if self.uart.any():  # Check if data is available
                response = self.uart.read().decode('utf-8')  # Read and decode the response
                print(f"Response: {response}")
            else:
                print("No response received")



wio_5 = WioE5()

# Send Data via LoRa
while True:
    print("Sending LoRa message...")
    wio_5.send_at_command("AT+MSG=\"Hello LoRa\"")  # Send a message
    sleep(20)  # Wait before sending the next message
