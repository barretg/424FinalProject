import board
import time
import adafruit_mcp4728

class PWMControl:
   
    ''' initialization '''
    def __init__(self):
        MCP4728_DEFAULT_ADDRESS = 0x60
        MCP4728A4_DEFAULT_ADDRESS = 0x64

        i2c = board.I2C()  # uses board.SCL and board.SDA
        # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
        #  use for MCP4728 variant
        #mcp4728 = adafruit_mcp4728.MCP4728(i2c, adafruit_mcp4728.MCP4728_DEFAULT_ADDRESS)
        #  use for MCP4728A4 variant
        self.mcp4728 = adafruit_mcp4728.MCP4728(i2c, adafruit_mcp4728.MCP4728A4_DEFAULT_ADDRESS)

        #neutral values set at beginning
        self.mcp4728.channel_a.value = int(65535 / 2)
        self.mcp4728.channel_b.value = int(65535 / 2)



    ''' gets the speed of the RC car '''
    def get_speed(self):
        pass
        
        # TODO: get speed

    ''' set throttle value given PWM percent '''
    def set_throttle_direct(self, percent):
        self.cur_throttle = percent

        # TODO: set throttle (duty cycle)

        '''
        with open('/dev/bone/pwm/1/a/duty_cycle', 'w') as throttle:
            # print(self.percent_to_period(percent))
            throttle.write(self.percent_to_period(percent))
        '''

    ''' set throttle value given rotational period for constant speed '''
    def set_throttle(self, rot_period: int):
        self.mcp4728.channel_b.value = rot_period
        pass

        '''      
        # if vehicle was previously stopped
        if rot_period == 0:
            print("rot_period 0")
            self.jumped = False

            self.set_throttle_direct(7.9)
            return 7.9

        # if vehicle was not previously stopped
        cur_rot_period = self.get_speed()
        print(cur_rot_period)
        diff = abs(cur_rot_period - rot_period)

        jump = 0
        if cur_rot_period == 1000000 and not self.jumped:
            print("Jumped")
            self.jumped = True
            jump = 0.05

        delta = 0.001

        # Speed is changed based on throttle error  
        if diff < 1:
            pass
        elif rot_period > cur_rot_period:
            self.set_throttle_direct(self.cur_throttle - (jump + self.diff_to_delta(diff)))
            print(f"Decreasing: {self.cur_throttle}")
            return self.cur_throttle
        elif rot_period < cur_rot_period:
            self.set_throttle_direct(self.cur_throttle + (jump + self.diff_to_delta(diff)))
            print(f"Increasing: {self.cur_throttle}")
            return self.cur_throttle
        '''

    ''' detect throttle error '''
    def diff_to_delta(self, diff):
        if diff < 30:
            return -0.0005
        elif diff < 25:
            return 0.0001
        elif diff < 400:
            return 0.0001
        else:
            return 0.0003

    ''' set steering '''
    def set_steering(self, percent: int):
        self.mcp4728.channel_a.value = percent
        

        '''
        with open('/dev/bone/pwm/1/b/duty_cycle', 'w') as steering:
            steering.write(self.percent_to_period(percent))
        return percent
        '''

    ''' shutdown '''
    def shutdown(self):
        print("Shutting down PWM...")   
        self.mcp4728.channel_b.value = int(65535 / 2)



        '''
        # Center steering and stop motor
        self.set_throttle_direct(7.5)
        self.set_steering(7.5)
        time.sleep(0.2)
        # Shut down throttle
        with open('/dev/bone/pwm/1/a/enable', 'w') as filetowrite:
            filetowrite.write('1')

        # Shut down steering
        with open('/dev/bone/pwm/1/b/enable', 'w') as filetowrite:
            filetowrite.write('0')

        # Close speed file
        self.speed.close()
        # self.last_rot.close()
        '''

    def percent_to_period(self, percent: float):
        return str(int(percent * 200000))




