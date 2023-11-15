import board
import busio
import adafruit_mcp4728

i2c = busio.I2C(board.SCL, board.SDA)
mcp4728 = adafruit_mcp4728.MCP4728(i2c, 0x64)

mcp4728.channel_a.value = 65535 # 3.3V
mcp4728.channel_b.value = int(65535/2) # 1.65V
mcp4728.channel_c.value = int(65535/4) # 0.825V
mcp4728.channel_d.value = 0 # 0V
