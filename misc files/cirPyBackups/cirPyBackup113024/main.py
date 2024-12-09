import board
import busio
import time
import math

import displayio
import adafruit_displayio_ssd1306

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

# Create a Group and add the TileGrid to it
group = displayio.Group()
group.append(tile_grid) # append() adds elements to splash and make them visible

# Show the group on the display
display.show(group)

def drawPixel(x, y, z):
    if 0 <= x < 128 and 0 <= y < 64:  # Make sure the pixel is within bounds
        bitmap[x, y] = int(z)
    #else:
       # assert False, "out of bounds bich"


# =============================================================================================================================



# Create a UART object using busio; timeout is the amount of time it will wait to take in info
uart = busio.UART(board.TX, board.RX, baudrate=230400, timeout=0.01)

# Buffer to hold a single packet of data (47 bytes)
packet_size = 47
packet = []

sampledData = [0] * 12



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

lastX = None
lastY = None
clearCounter = 0        # counts the amount of plotted pixels before clearing screen
timeConst = 2000          # value clearCounter needs to surpass to clear screen

# Function to update plot based on angle and distance
def updatePlot(i):
    global lastX, lastY
    global clearCounter
    
    if (27000 <= i[1] <= 36000) or (0 <= i[1] <= 9000):
        # Get the angle and distance from the data
        angle = ( 9000 - i[1]) / 100.0  # Convert angle from scaled value (e.g., 9000 = 90°) to degrees
        distance = i[0]  # Distance value
        
        # Convert angle to radians (since math functions use radians)
        angle_radians = math.radians(angle)

        # Center of the screen
        xMid = 63
        yMid = 55  # center the LiDAR to the car on the screen

        scaleDown = 5

        # Calculate the X and Y positions using polar-to-Cartesian conversion
        x = xMid + int(distance * math.cos(angle_radians) / scaleDown)  # Scaling distance down
        y = yMid - int(distance * math.sin(angle_radians) / scaleDown)  # Invert Y-axis for OLED display

        # print(str(x) + '  ' + str(y))

        if 0 <= x <= 127 and 0 <= y <= 63:
            drawPixel(x, y, 1)
        clearCounter += 1
        if clearCounter >= timeConst:
            clearScreen()
            drawCar()
            clearCounter = 0






# lidar sensor code
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

                for i in range(12): # 12 sets of 3 starting at index 6 (dLSB, dMSB, sig)
                    sampledData[i] = [curPack[3*i+6] + 256*curPack[3*i+7] , (totalAngle*(i))//12 + startAngle , curPack[3*i+8] ,curPack[45]*256 + curPack[44]]

                for i in sampledData:
                    updatePlot(i)
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
