import board
import time
import random
import displayio
import adafruit_displayio_ssd1306
import busio
import espnow #type: ignore
import math
import json
from digitalio import DigitalInOut, Direction

'''
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

# =============================================================================================================================
# display initialization 

refreshRate = 3
scaleDown = 10 # variable to adjust to zoom in or out on the screen
scdl = 10
scdm = 25
scdh = 100
leftButton = DigitalInOut(board.IO1)
leftButton.direction = Direction.INPUT
rightButton = DigitalInOut(board.IO2)
rightButton.direction = Direction.INPUT
pLeftButton = False
pRightButton = False

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
    if 0 <= x < 128 and 0 <= y < 64:  # will only draw pixels within bounds
        if bitmap[x,y] != int(z):
            bitmap[x, y] = int(z)

def drawCar():
    global scaleDown
    carPixels = set()
    height = 58 # y coord 

# real distance in mm / scaleDown = pixelPlot
# 8000/10 = 800 (too far at this scaleDown value)
# 8000/x = 440 (find x for it to be at the midpoint) (x = 18.18)
# 8000/100 = 80 ( < 127, will fit on screen)

# 2000/10 = 200
# 2000/18.18 = 110
# 2000/100 = 20

# 1000/10 = 100 
# 1000/18.18 = 55
# 1000/100 = 10 

    if scaleDown == scdh:
        for i in range(57,69): # bumper width
            carPixels.add((i,height)) # bumper height
        for i in range(height + 1,64): # left side height
            carPixels.add((56,i)) # left side x coord
        for i in range(height + 1,64): # right side height
            carPixels.add((69,i)) # right side x coord

    elif scaleDown == scdm:
        # 28
        carPixels.add((28,height+5))
        carPixels.add((29,height+4))
        carPixels.add((29,height+3))
        for i in range(30,32):
            carPixels.add((i,height+2)) 
        for i in range(32,50):
            carPixels.add((i,height+1)) 
        for i in range(50,77): # bumper width
            carPixels.add((i,height)) # bumper height
        for i in range(77,95): # bumper width
            carPixels.add((i,height+1)) # bumper height
        for i in range(95,97):
            carPixels.add((i,height+2))
        carPixels.add((97,height+3))
        carPixels.add((97,height+4))
        carPixels.add((98,height+5))
        
    elif scaleDown == scdl:
        for i in range(57,69): # bumper width
            carPixels.add((i,height)) # bumper height
        for i in range(height + 1,64): # left side height
            carPixels.add((56,i)) # left side x coord
        for i in range(height + 1,64): # right side height
            carPixels.add((69,i)) # right side x coord
        for i in range(59,67):
            carPixels.add((i,63))

        # carPixels.add((63,height+5))
        # 98

    for x in carPixels:
        bitmap[x] = 1
drawCar()
# 0 - 57 is the y range because the car bumper goes to y = 58 - 63

def clearScreen():
    global timeSinceReset
    bitmap.fill(0)
    drawCar()
    timeSinceReset = time.monotonic()

timeSinceReset = time.monotonic()

# Function to update plot based on angle and distance
def updatePlot(i):
    curTime = time.monotonic()
    global timeSinceReset, scaleDown
    
    if (27000 <= i[1] <= 36000) or (0 <= i[1] <= 9000):
        # Get the angle and distance from the data
        angle = ( 9000 - i[1]) / 100.0  # Convert angle from scaled value (e.g., 9000 = 90Â°) to degrees
        distance = i[0]  # Distance value
        
        # Convert angle to radians (since math functions use radians)
        angle_radians = math.radians(angle)

        # Center of the screen
        xMid = 63
        yMid = 57  # center the LiDAR to the car on the screen

        # polar to cartesian conversion
        x = xMid + int(distance * math.cos(angle_radians) / scaleDown)
        y = yMid - int(distance * math.sin(angle_radians) / scaleDown)  # Invert Y-axis



        drawPixel(x,y,1)  # Run the expression for each (x, y) pair
        if (curTime - timeSinceReset >= refreshRate):
            clearScreen()
#-------------------------------------------------------------------------
#Receiver Wireless Code Start
#import espnow, time

e = espnow.ESPNow()
packets = []
print("Initializing ESP-NOW Receiver...")
while True:
    # Read any incoming message
    if e:
        message = e.read()
        #print(type(message))
        #print("Received message:", message.msg)
        decoded_data = message.msg.decode('utf-8')  # Decode from bytes to string
        original_element = json.loads(decoded_data)  # Deserialize the JSON string back to the original element
        if isinstance(original_element,list) and original_element[0] != 0 and original_element[1] != 0:
            updatePlot(original_element)


        # more efficient but too volatile
        # # print(original_element)
        # if isinstance(original_element,str) and len(original_element) == 120:
        #     # print(original_element) 
        #     for i in range(0, len(original_element), 10):
        #         num1 = int(original_element[i:i+5])
        #         num2 = int(original_element[i+5:i+10])
        #         updatePlot([num1, num2])


    # Add a small delay to avoid overwhelming the loop
    time.sleep(0.001)  # Adjust sleep time as needed
    if leftButton.value == False and pLeftButton == True: # scaleDown go up
        if scaleDown == scdl:
            scaleDown = scdm
        elif scaleDown == scdm:
            scaleDown = scdh
        clearScreen()
    if rightButton.value == False and pRightButton == True: # scaleDown go down
        if scaleDown == scdm:
            scaleDown = scdl
        elif scaleDown == scdh:
            scaleDown = scdm
        clearScreen()
    pLeftButton = leftButton.value
    pRightButton = rightButton.value

#Receiver Wireless Code Ends
#-------------------------------------------------------------------------