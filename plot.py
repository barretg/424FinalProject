import matplotlib.pyplot as plt
import numpy as np

from data import error_data, throttle_pwm_data, steering_pwm_data, proportional_resp_data, derivative_resp_data

# Plots relevant values throughout the run of the RC car
frames = np.arange(len(error_data))
plt.plot(frames, error_data, throttle_pwm_data, steering_pwm_data)
plt.show()
