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
cs = board.IO26 #IO26
dc = board.IO47 #IO47
reset = board.IO33 #IO33
spi = busio.SPI(board.IO46, MOSI=board.IO45) #initialize bus
display_bus = displayio.FourWire(spi, command=dc, chip_select=cs,
                                 reset=reset, baudrate=1000000)
#SDA IO45
#SCK IO46

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
        time.sleep(0.2)
        bitmap[x, y] = 0 #turn off pixel

# Draw some test pixels
#draw_pixel(random.randint(0,128), random.randint(0,64), 1)  # Draw a white pixel at (10, 10)

# To update display, we don’t need anything else because displayio handles it automatically
while True:
    draw_pixel(random.randint(0,128), random.randint(0,64), 1)  # Draw a white pixel at (10, 10)
    time.sleep(0.1)