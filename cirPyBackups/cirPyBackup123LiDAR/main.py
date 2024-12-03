
import board
import busio
import time
import math

# screen libraries
import displayio
import adafruit_displayio_ssd1306 

import espnow, time # type: ignore

import json # packing data to send wirelessly

from digitalio import DigitalInOut, Direction # troubleshooting LEDS

crashLED = DigitalInOut(board.IO18)
crashLED.direction = Direction.OUTPUT
crashLED.value = False

# =============================================================================================================================
# wireless communication initialization

e = espnow.ESPNow()
peer = espnow.Peer(b'\x48\xCA\x43\x5F\xAF\x90')
e.peers.append(peer)
print("Initializing ESP-NOW Sender...")
timeAtRun = time.monotonic()

# =============================================================================================================================
# display initialization

displayio.release_displays() #release pins

# Set up the SPI or I2C connection (depending on your setup)
cs = board.IO26 #IO26
dc = board.IO47 #IO47
reset = board.IO33 #IO33
spi = busio.SPI(board.IO46, MOSI=board.IO45) #initialize bus
display_bus = displayio.FourWire(spi, command=dc, chip_select=cs, reset=reset, baudrate=230400) # 1000000
#SDA IO45
#SCK IO46

# Create the display object
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

splash = displayio.Group() #Manage a group of sprites and groups and how they are inter-related.
display.show(splash)

# Create a bitmap where we can draw pixels
bitmap = displayio.Bitmap(128, 64, 2)  # 128x64 pixels, 2 colors (black and white)
palette = displayio.Palette(2)
palette[0] = 0x000000  # Black
palette[1] = 0xFFFFFF  # White

# Create a TileGrid to hold the bitmap
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)

# # Create a Group and add the TileGrid to it
group = displayio.Group()
group.append(tile_grid) # append() adds elements to splash and make them visible

# Show the group on the display 
display.show(group)

def drawPixel(x, y, z):
    if 0 <= x < 128 and 0 <= y < 64:  # will only draw pixels within bounds
        bitmap[x, y] = int(z)

def drawCar():
    carPixels = ((57,56),(58,56),(59,56),(60,56),(61,56),(62,56),(63,56),(64,56),(65,56),(66,56),(67,56),(68,56), # bumper
             (56,57),(56,58),(56,59),(56,60),(56,61),(56,62),(56,63),(69,57),(69,58),(69,59),(69,60),(69,61),(69,62),(69,63), # sides
             (60,62),(61,62),(62,62),(63,62),(64,62),(65,62),(59,63),(66,63),(57,57),(68,57)) # window
    for x in carPixels:
        bitmap[x] = 1
drawCar()

# 0 - 55 is the y range because the car bumper goes to y = 56 - 63

def clearScreen():
    bitmap.fill(0)

# 1d distance troubleshooting
lastX = None
lastY = None
timeSinceReset = time.monotonic()
timeSinceReset1 = time.monotonic()

# clearCounter = 0        # counts the amount of plotted pixels before clearing screen
timeConst = 2000          # value clearCounter needs to surpass to clear screen

# Function to update plot based on angle and distance
def updatePlot(i):
    curTime = time.monotonic()
    global timeSinceReset
    printSet = set()
    
    if (27000 <= i[1] <= 36000) or (0 <= i[1] <= 9000):
        # Get the angle and distance from the data
        angle = ( 9000 - i[1]) / 100.0  # Convert angle from scaled value (e.g., 9000 = 90°) to degrees
        distance = i[0]  # Distance value
        
        # Convert angle to radians (since math functions use radians)
        angle_radians = math.radians(angle)

        # Center of the screen
        xMid = 63
        yMid = 55  # center the LiDAR to the car on the screen

        scaleDown = 5 # variable to adjust to zoom in or out on the screen

        # polar to cartesian conversion
        x = xMid + int(distance * math.cos(angle_radians) / scaleDown)
        y = yMid - int(distance * math.sin(angle_radians) / scaleDown)  # Invert Y-axisnnnnnnnnnnnnnnnn



#        drawPixel(x,y,1)  # Run the expression for each (x, y) pair
        if (curTime - timeSinceReset >= 1):
#            clearScreen()
#            drawCar()
            timeSinceReset = time.monotonic()
            e.send(b'ojsdfjh')

# =============================================================================================================================
# LiDAR sensor initialization

# Create a UART object using busio; timeout is the amount of time it will wait to take in info
uart = busio.UART(board.TX, board.RX, baudrate=230400, timeout=0.01)

# Buffer to hold a single packet of data (47 bytes)
packet_size = 47
packet = []

sampledData = [0] * 12

prevData = 0

import espidf

# main function =============================================
while True:
    # time.sleep(1)
    # print('saoidfo')


    # intake lidar data
    # =============================================================================================================================

    if uart.in_waiting > 0:
        # 'data' holds however many bytes that are waiting in the "buffer" memory, adds it to 'packet'
        data = uart.read(uart.in_waiting)
        packet.extend(data)

        while len(packet) >= packet_size:
            # Extract the first 47 bytes from the packet buffer
            curPack = packet[:packet_size]
            packet = packet[packet_size:]  # Remove processed bytes from the packet buffer

            # Check start byte
            if curPack[0] == 0x54:
                # current
                # print("radar speed:", end = " ")
                # print(curPack[3]*256 + curPack[2])

                startAngle = curPack[5]*256 + curPack[4]
                endAngle = curPack[43]*256 + curPack[42]

                totalAngle = endAngle - startAngle

                # inbetween packet data structure: 
                # dtype: [distance, angle, strength, time]
                # position of motor is when angle ~= 0 or 360

                #  [curPack[3*i+6] + 256*curPack[3*i+7] , (totalAngle*(i))//12 + startAngle , curPack[3*i+8] ,curPack[45]*256 + curPack[44]]

                for i in range(12): # 12 sets of 3 starting at index 6 (dLSB, dMSB, sig)
                    distToAngle = (totalAngle*(i))//12 + startAngle
                    if ((27000 <= distToAngle <= 36000) or (0 <= distToAngle <= 9000)):
                        sampledData[i] = [curPack[3*i+6] + 256*curPack[3*i+7] , distToAngle]
                    
                # print(sampledData)
                # longInt = ""
                # for sublist in sampledData:
                #     if isinstance(sublist, list):
                #         longInt += f"{sublist[0]:05d}{sublist[1]:05d}"
                # print(longInt)
                # print(len(longInt))



                # if (time.monotonic() - timeSinceReset1 >= .01):
                #     print(time.monotonic() - timeSinceReset1)
                #     msgSend = json.dumps(longInt).encode('utf-8')
                #     try:
                #         e.send(msgSend)  # Attempt to send the long integer
                #         crashLED.value = False
                #         print("sent")
                #     except espidf.IDFError as error:
                #         # Check if the error is the specific ESP-NOW error you're encountering
                #         if "ESP-NOW error 0x306a" in str(error):
                #             crashLED.value = True  # Turn on the crash LED
                #             print("Error: ESP-NOW error 0x306a occurred, crashLED activated.")
                #         else:
                #             # If the error is not the expected one, raise it again
                #             raise
                #     # print(msgSend)
                #     timeSinceReset1 = time.monotonic()
                # prevData = longInt


                # ansRes = [] 
                # for i in range(0, len(longInt), 10):# longInt = e.read()
                #     num1 = int(longInt[i:i+5])
                #     num2 = int(longInt[i+5:i+10])
                #     ansRes.append([num1, num2])
                
                # print(ansRes)
                

                for i in sampledData:
                    if (time.monotonic() - timeSinceReset1 >= .01):
                        timeSinceReset1 = time.monotonic()
                        msgSend = json.dumps(i).encode('utf-8')
                        try:
                            e.send(msgSend)  # Attempt to send the long integer 
                            crashLED.value = False
                        except espidf.IDFError as error:
                            if "ESP-NOW error 0x306a" in str(error):
                                crashLED.value = True
                                print("Error: ESP-NOW error 0x306a occurred, crashLED activated.")
                            else:
                                raise


                    # updatePlot(i)
                        # (i[1] > 17980) and (i[1] < 18020)      (i[1] > 7980) and (i[1] < 8020)     (i[1] > 35960) and (i[1] < 100)
                        # print('towards battery: ' + str(i[0]) + '   strength: '+ str(i[2]))


                        # xMid = 63
                        # divConst = 50
                        # plotY = i[0]//divConst
                        # print(str(plotY) + " " + str(lastY))


                        # if plotY < 63 and lastY != plotY:
                        #     drawPixel(xMid,55-lastY,0)
                        #     drawPixel(xMid,55-plotY,1)
                        #     lastY = plotY

                            

                # for i in sampledData:
                #     if ((i[1] < 100) or (i[1] > 35900) ):
                #         print('towards motor: ' + str(i[0]) + '   strength: '+ str(i[2]))



                # 54 2C 74 08 B0 86 00 00 D4 00 00 D4 00 00 D4 00 00 D4 00 00 D4 00 00 D5 00 00 D5 00 00 49 00 00 5F 00 00 B0 00 00 D2 00 00 D4 02 89 1E 09 1F

                # print("start angle:", end = " ")
                # print(curPack[5]*256 + curPack[4])
                # print("end angle:  ", end = " ")
                # print(curPack[43]*256 + curPack[42])

                # print("time:", end = " ")
                # print(curPack[45]*256 + curPack[44])

                # Print the packet as space-separated hex values, newline per packet =================
                # for byte in curPack:
                #     print(f"{byte:02X}", end=" ")
                # print()

            else:
                # If the first byte is not 0x54, skip the first byte and check the next one
                # will loop until the packet size falls below 47, at which point you add the bytes waiting in buffer
                packet = packet[1:]






# THIS IS HOW TO DO NONBLOCKING

# import time
# timeAtRun = time.monotonic()
# while True:
#     print(time.monotonic() - timeAtRun)
#     time.sleep(1/3)








# ==========================================================================================================================
# ==========================================================================================================================
# ==========================================================================================================================
# ==========================================================================================================================
# ==========================================================================================================================
# ==========================================================================================================================
# ==========================================================================================================================







# import board, time, touchio, digitalio, touchio
# #---------------------------------------------------------------------------------
# #Sender Bluetooth
# from adafruit_ble import BLERadio
# from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
# from adafruit_ble.services.nordic import UARTService
# from adafruit_bluefruit_connect.raw_text_packet import RawTextPacket

# # IMPORTANT: This must be 11 char or less or your code WILL NOT WORK
# # name of advertised device that we are seeking:
# receiver_name = "profg-r" #it looks for receiver name and send data

# ble = BLERadio() #create a bluetooth object
# uart_connection = None #we haven't connect anything yet

# def send_packet(uart_connection_name, packet): #send packet to the name, this is the function send data
#     # Try to send packet, if success return true
#     """Returns False if no longer connected."""
#     try:
#         uart_connection_name[UARTService].write(packet.to_bytes()) #try to send packet as bytes
#     except:  # pylint: disable=bare-except
#         try:
#             uart_connection[UARTService].write(packet) #otherwise try to send the packet directly, usualy used for raw text
#         except:  # pylint: disable=bare-except
#             try:
#                 uart_connection_name.disconnect()
#             except:  # pylint: disable=bare-except
#                 pass
#             print("No longer connected")
#             return False
#     return True 

# while True: #loop over and over, send data when there is new packet
#     if not uart_connection or not uart_connection.connected:  # If not connected...Scan for connections
#         print("Scanning...")
#         for adv in ble.start_scan(ProvideServicesAdvertisement, timeout=5):  # Scan...
#             if UARTService in adv.services:  # If UARTService found...
#                 if adv.complete_name == receiver_name: #check if receiver name matches exactly as above
#                     uart_connection = ble.connect(adv)  # Create a UART connection...
#                     print(f"I've found and connected to {receiver_name}!")
#                     break # MUST include this here or code will never continue after connection.
#         # Stop scanning whether or not we are connected.
#         ble.stop_scan()  # And stop scanning.

#     while uart_connection and uart_connection.connected:  # If connected...Send packet
#         user_input = input("Enter text to send: ")+"\r\n"
#         if not send_packet(uart_connection, user_input):
#             uart_connection = None
#             continue
#         print(f"Just sent message {user_input}")
# #---------------------------------------------------------------------------------
# #Sender Bluetooth Ends 

# #---------------------------------------------------------------------------------
# #Receiver Bluetooth
# import board, digitalio

# # ================================
# # BLUETOOTH SETUP CODE & FUNCTIONS
# # ================================

# from adafruit_ble import BLERadio
# from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
# from adafruit_ble.services.nordic import UARTService

# from adafruit_bluefruit_connect.packet import Packet
# from adafruit_bluefruit_connect.raw_text_packet import RawTextPacket

# # Setup BLE connection
# ble = BLERadio()
# uart = UARTService()
# advertisement = ProvideServicesAdvertisement(uart)
# # Give your CPB a unique name between the quotes below.
# # This MUST be the same name - same spelling & capitalization
# # as the name in the "receiver_name = " line in the SENDER's code.py file.
# # VERY IMPORTANT - the name must also be <= 11 characters!
# advertisement.complete_name = "profg-r" #This should match the string in the sender code receiver_name
# ble.name = advertisement.complete_name

# # === END OF BLUETOOTH SETUP CODE & FUNCTIONS ===


# print("Running Receiver Code!") 
# while True:
#     ble.start_advertising(advertisement)  # Start advertising. The sender looks for advertisement with the receiver_name
#     print(f"Advertising as: {advertisement.complete_name}") # Name prints once each time the board isn't connected
#     was_connected = False

#     while not was_connected or ble.connected:
#         if ble.connected:  # If BLE is connected...
#             was_connected = True

#             if uart.in_waiting:  # Check to see if any new data has been sent from the SENDER.
#                 try:
#                     packet = Packet.from_stream(uart)  # Create the packet object.
#                 except ValueError:
#                     continue
#                 # Note: I could have sennt ColorPackets that would have had colors, but I wanted
#                 # to show ButtonPackets because you could do non-color things here, too. For example,
#                 # if Button_1, then move a servo, if Button_2, then play a certain sound, etc.
#                 if isinstance(packet, RawTextPacket): #isinstance() checks what type of packet it is
#                     print(f"Message Received: {packet.text.decode().strip()}")

#     # If we got here, we lost the connection. Go up to the top and start
#     # advertising again and waiting for a connection.
# #---------------------------------------------------------------------------------
# #Receiver Bluetooth Ends
'''

#-------------------------------------------------------------------------
#Sender Wireless Code Start
# import espnow, time # type: ignore

# e = espnow.ESPNow()
# peer = espnow.Peer(b'\x48\xCA\x43\x5F\xAF\x90')
# e.peers.append(peer)
# print("Initializing ESP-NOW Sender...")

# counter = [0,1,2,4,5,6,7,7,2,2,4,57,87,2,2,89,94,5,6]

# while True:
#     e.send(str(counter))
#     counter[0] += 1
#     time.sleep(0.1)
#Sender Wireless Code Ends
#-------------------------------------------------------------------------

'''