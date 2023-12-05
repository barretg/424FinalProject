#COMP 424 Project 3 inspired by “Autonomous Lane-Keeping Car Using Raspberry
# Pi and OpenCV”. Instructables. URL: https://www.instructables.com/Autonomous-Lane-Keeping-Car-Using-Raspberry-Pi-and/

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
import time
import adafruit_mcp4728

MCP4728_DEFAULT_ADDRESS = 0x60
MCP4728A4_DEFAULT_ADDRESS = 0x64

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
#  use for MCP4728 variant
#mcp4728 = adafruit_mcp4728.MCP4728(i2c, adafruit_mcp4728.MCP4728_DEFAULT_ADDRESS)
#  use for MCP4728A4 variant
mcp4728 = adafruit_mcp4728.MCP4728(i2c, adafruit_mcp4728.MCP4728A4_DEFAULT_ADDRESS)

#neutral values set at beginning
mcp4728.channel_a.value = int(65535 / 2)
mcp4728.channel_b.value = int(65535 / 2)
for i in range(0, 2):
    #forward
    mcp4728.channel_b.value = int(65535 / 2.5)
    time.sleep(1)
    #stop
    mcp4728.channel_b.value = int(65535 / 2)
    time.sleep(1)

for i in range(0, 2):
    #backward
    mcp4728.channel_b.value = int(65535 / 1.5)
    time.sleep(1)
    #stop
    mcp4728.channel_b.value = int(65535 / 2)
    time.sleep(1)

for i in range(0, 2):
    #left
    mcp4728.channel_a.value = int(65535 / 2.5)
    time.sleep(1)
    #neutral
    mcp4728.channel_a.value = int(65535 / 2)
    time.sleep(1)
    #right
    mcp4728.channel_a.value = int(65535 / 1.5)
    time.sleep(1)
    #neutral
    mcp4728.channel_a.value = int(65535 / 2)

#mcp4728.channel_b.value = 65535
#time.sleep(2);
#mcp4728.channel_b.value = 0

#mcp4728.channel_c.value = 65535
#time.sleep(2);
#mcp4728.channel_c.value = 0

#mcp4728.channel_d.value = 65535
#time.sleep(2);
#mcp4728.channel_d.value = 0



#mcp4728.channel_a.value = 65535  # Voltage = VDD
#mcp4728.channel_b.value = int(65535 / 2)  # VDD/2
#mcp4728.channel_c.value = int(65535 / 4)  # VDD/4
#mcp4728.channel_d.value = 0  # 0V
