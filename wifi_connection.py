import network
SSID = b'TP-LINK_2D72'
wlan = network.WLAN(network.STA_IF) # create station interface
wlan.active(True)       # activate the interface
wifi = wlan.scan()
if SSID in wifi[:][0]:
  wlan.connect('TP-LINK_2D72','09260450')
  if wlan.isconnected():
    print(f'\n ESP32 is connected to {str(SSID).split("'")[1]}')
    print(f'\n {wlan.ifconfig()}')