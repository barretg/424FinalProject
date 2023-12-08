import matplotlib.pyplot as plt
import numpy as np

from data import error_data, throttle_pwm_data, steering_pwm_data, proportional_resp_data, derivative_resp_data

# Plots relevant values throughout the run of the RC car
frames = np.arange(len(throttle_pwm_data))
plt.figure(figsize=(10, 10))
plt.plot(frames, throttle_pwm_data, label="throttle values")
plt.plot(frames, error_data, label="error")
plt.plot(frames, steering_pwm_data, label="steering values")
plt.legend()
plt.show()

# Plots relevant values throughout the run of the RC car
frames = np.arange(len(throttle_pwm_data))
plt.figure(figsize=(10, 10))
plt.plot(frames, proportional_resp_data, label="proportional response")
plt.plot(frames, error_data, label="error")
plt.plot(frames, derivative_resp_data, label="derivative response")
plt.legend()
plt.show()

