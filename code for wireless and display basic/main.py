'''
import board
import time
import random
import displayio
import adafruit_displayio_ssd1306
import busio

displayio.release_displays() #release pins

WIDTH = 128
HEIGHT = 64
BORDER = 5

# Set up the SPI or I2C connection (depending on your setup)
cs = board.IO26 #IO26, chip select
dc = board.IO47 #IO47, data address
reset = board.IO33 #IO33, reset pin
spi = busio.SPI(board.IO46, MOSI=board.IO45) #initialize bus
display_bus = displayio.FourWire(spi, command=dc, chip_select=cs,
                                 reset=reset, baudrate=1000000)
#SDA IO45, MOSI
#SCK IO46, clock

# Create the display object
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

splash = displayio.Group() #Manage a group of sprites and groups and how they are inter-related.
display.show(splash)

# Create a bitmap where we can draw pixels
bitmap = displayio.Bitmap(128, 64, 2)  # 128x64 pixels, 2 colors (black and white)
palette = displayio.Palette(2)
palette[0] = 0x000000  # Black
palette[1] = 0xFFFFFF  # White

# Create a TileGrid to hold the bitmap
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)

# Create a Group and add the TileGrid to it
group = displayio.Group()
group.append(tile_grid) # append() adds elements to splash and make them visible

# Show the group on the display
display.show(group)

# Function to draw a single pixel
def draw_pixel(x, y, color):
    if 0 <= x < 128 and 0 <= y < 64:  # Make sure the pixel is within bounds
        bitmap[x, y] = color
        time.sleep(0.1)
        #bitmap[x, y] = 0 #turn off pixel

def turnoff_pixel(x, y, color):
    if 0 <= x < 128 and 0 <= y < 64:  # Make sure the pixel is within bounds
        bitmap[x, y] = 0
        # time.sleep(0.2)
        # bitmap[x, y] = 0 #turn off pixel

# Draw some test pixels
#draw_pixel(random.randint(0,128), random.randint(0,64), 1)  # Draw a white pixel at (10, 10)

# To update display, we don’t need anything else because displayio handles it automatically
while True:
    for x in range(128):
        draw_pixel(x, 0, 1)  # Draw a white pixel at (10, 10)
        #time.sleep(0.1)
    for x in range(128):
        turnoff_pixel(x,0,0)
    #draw_pixel(random.randint(0,128), random.randint(0,64), 1)  # Draw a white pixel at (10, 10)
    time.sleep(0.1)
'''

'''
#---------------------------------------------------------------------------------
#Sender Bluetooth
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from adafruit_bluefruit_connect.raw_text_packet import RawTextPacket

# IMPORTANT: This must be 11 char or less or your code WILL NOT WORK
# name of advertised device that we are seeking:
receiver_name = "profg-r" #it looks for receiver name and send data

ble = BLERadio() #create a bluetooth object
uart_connection = None #we haven't connect anything yet

def send_packet(uart_connection_name, packet): #send packet to the name, this is the function send data
    # Try to send packet, if success return true
    """Returns False if no longer connected."""
    try:
        uart_connection_name[UARTService].write(packet.to_bytes()) #try to send packet as bytes
    except:  # pylint: disable=bare-except
        try:
            uart_connection[UARTService].write(packet) #otherwise try to send the packet directly, usualy used for raw text
        except:  # pylint: disable=bare-except
            try:
                uart_connection_name.disconnect()
            except:  # pylint: disable=bare-except
                pass
            print("No longer connected")
            return False
    return True 

while True: #loop over and over, send data when there is new packet
    if not uart_connection or not uart_connection.connected:  # If not connected...Scan for connections
        print("Scanning...")
        for adv in ble.start_scan(ProvideServicesAdvertisement, timeout=5):  # Scan...
            if UARTService in adv.services:  # If UARTService found...
                if adv.complete_name == receiver_name: #check if receiver name matches exactly as above
                    uart_connection = ble.connect(adv)  # Create a UART connection...
                    print(f"I've found and connected to {receiver_name}!")
                    break # MUST include this here or code will never continue after connection.
        # Stop scanning whether or not we are connected.
        ble.stop_scan()  # And stop scanning.

    while uart_connection and uart_connection.connected:  # If connected...Send packet
        user_input = input("Enter text to send: ")+"\r\n"
        if not send_packet(uart_connection, user_input):
            uart_connection = None
            continue
        print(f"Just sent message {user_input}")
#---------------------------------------------------------------------------------
#Sender Bluetooth Ends
'''


'''
import board, digitalio

# ================================
# BLUETOOTH SETUP CODE & FUNCTIONS
# ================================

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.raw_text_packet import RawTextPacket

# Setup BLE connection
ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)
# Give your CPB a unique name between the quotes below.
# This MUST be the same name - same spelling & capitalization
# as the name in the "receiver_name = " line in the SENDER's code.py file.
# VERY IMPORTANT - the name must also be <= 11 characters!
advertisement.complete_name = "profg-r"
ble.name = advertisement.complete_name

# === END OF BLUETOOTH SETUP CODE & FUNCTIONS ===

print("Running Receiver Code!") 
while True:
    ble.start_advertising(advertisement)  # Start advertising.
    print(f"Advertising as: {advertisement.complete_name}") # Name prints once each time the board isn't connected
    was_connected = False

    while not was_connected or ble.connected:
        if ble.connected:  # If BLE is connected...
            was_connected = True

            if uart.in_waiting:  # Check to see if any new data has been sent from the SENDER.
                try:
                    packet = Packet.from_stream(uart)  # Create the packet object.
                except ValueError:
                    continue
                if isinstance(packet, RawTextPacket):
                    print(f"Message Received: {packet.text.decode().strip()}")

    # If we got here, we lost the connection. Go up to the top and start
    # advertising again and waiting for a connection.
'''

#-------------------------------------------------------------------------
#Receiver Wireless Code Start
import espnow, time

e = espnow.ESPNow()
packets = []
print("Initializing ESP-NOW Receiver...")
while True:
    # Read any incoming message
    if e:
        message = e.read()
        print("Received message:", message)
    
    # Add a small delay to avoid overwhelming the loop
    time.sleep(0.1)  # Adjust sleep time as needed
#Receiver Wireless Code Ends
#-------------------------------------------------------------------------
