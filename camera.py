'''

ELEC 424 Final Project - Autonomous Lanekeeping RC Car
Team YoungerWoods (ft. The NicoMobile)

GitHub Repo:
https://github.com/nicorossirice/comp424-FinalProject/tree/main

Hackster Webpage:
https://www.hackster.io/team-youngerwoods/the-nicomobile-83caa9

Used the following reference code: 
https://www.instructables.com/Autonomous-Lane-Keeping-Car-Using-Raspberry-Pi-and/
https://www.hackster.io/really-bad-idea/autonomous-path-following-car-6c4992

'''

import math
import signal
import time
import cv2
import matplotlib.pyplot as plt
import numpy as np
from pwm_control import PWMControl

# from pwm_control import PWMControl


''' BLUE LINE DETECTION '''

def detect_edges(frame):
    # filter for blue lane lines
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #cv2.imshow("HSV",hsv)
    lower_blue = np.array([70, 80, 0], dtype = "uint8")
    upper_blue = np.array([150, 255, 255], dtype="uint8")
    mask = cv2.inRange(hsv,lower_blue,upper_blue)
    #cv2.imshow("mask",mask)
    
    # detect edges
    edges = cv2.Canny(mask, 50, 100)
    cv2.imshow("edges",edges)
    
    return edges

def region_of_interest(edges):
    height, width = edges.shape
    mask = np.zeros_like(edges)

    # only focus lower half of the screen
    polygon = np.array([[
        (0, height),
        (0,  height/2),
        (width , height/2),
        (width , height),
    ]], np.int32)
    
    cv2.fillPoly(mask, polygon, 255)
    
    cropped_edges = cv2.bitwise_and(edges, mask)
#    cv2.imshow("roi",cropped_edges)
    
    return cropped_edges

def detect_line_segments(cropped_edges):
    rho = 1  
    theta = np.pi / 180  
    min_threshold = 10  
    
    line_segments = cv2.HoughLinesP(cropped_edges, rho, theta, min_threshold, 
                                    np.array([]), minLineLength=5, maxLineGap=150)

    return line_segments

def average_slope_intercept(frame, line_segments):
    lane_lines = []
    
    if line_segments is None:
        print("no line segments detected")
        return lane_lines

    height, width,_ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    left_region_boundary = width * (1 - boundary)
    right_region_boundary = width * boundary
    
    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            if x1 == x2:
                print("skipping vertical lines (slope = infinity")
                continue
            
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - (slope * x1)
            
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    return lane_lines

def make_points(frame, line):
    height, width, _ = frame.shape
    
    slope, intercept = line
    
    y1 = height  # bottom of the frame
    y2 = int(y1 / 2)  # make points from middle of the frame down
    
    if slope == 0:
        slope = 0.1
        
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)
    
    return [[x1, y1, x2, y2]]

def display_lines(frame, lines, line_color=(0, 255, 0), line_width=6):
    line_image = np.zeros_like(frame)
    
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
                
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    
    return line_image

def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5 ):
    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape
    
    steering_angle_radian = steering_angle / 180.0 * math.pi
    
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)
    
    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)
    
    return heading_image

def get_steering_angle(frame, lane_lines):
    
    height,width,_ = frame.shape
    
    if len(lane_lines) == 2:
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        mid = int(width / 2)
        x_offset = (left_x2 + right_x2) / 2 - mid
        y_offset = int(height / 2)
        
    elif len(lane_lines) == 1:
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
        y_offset = int(height / 2)
        
    elif len(lane_lines) == 0:
        x_offset = 0
        y_offset = int(height / 2)
        
    angle_to_mid_radian = math.atan(x_offset / y_offset)
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  
    steering_angle = angle_to_mid_deg + 90
    
    return steering_angle



''' STOP SIGN DETECTION '''
# currently for [145, 135, 140] - [175, 150, 200]
# background redpx values could be <1000
# detection could be between 1000-25000
def check_for_stop_sign(frame):
    
    # Range of red in HSV
    left_lower_red = np.array([145, 135, 140], dtype="uint8")
    left_upper_red = np.array([175, 150, 200], dtype="uint8")
    right_lower_red = np.array([150, 145, 160], dtype="uint8")
    right_upper_red = np.array([170, 150, 180], dtype="uint8")
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


    # Right orientation for HSV function
    left_lower_red = np.flip(left_lower_red)
    left_upper_red = np.flip(left_upper_red)
    right_lower_red = np.flip(right_lower_red)
    right_upper_red = np.flip(right_upper_red)

    # Create mask for 'red' detection
    left_mask = cv2.inRange(frame, left_lower_red, left_upper_red)
    right_mask = cv2.inRange(frame, right_lower_red, right_upper_red)
    mask = cv2.bitwise_or(left_mask, right_mask)
    num_red_px = cv2.countNonZero(mask)
    
    '''
    Average HSV value for red construction paper: 
    125.98791666666666
    107.065
    163.78041666666667
    '''

    # TESTING: 
    center = frame[:, :, :]
    # center[:110, :, :] = 0
    # center[130:, :, :] = 0
    # center[:, :110, :] = 0
    # center[:, 230:, :] = 0
    # center = center[110:130, 110:230, :]
    # print(np.mean(center[:,:,0]))
    # print(np.mean(center[:,:,1]))
    # print(np.mean(center[:,:,2]))

    # print(np.average(center[110:130, 110:230, :], axis=1))

    # cv2.imshow("center", center)

    # print(frame.shape)
    # Filter out non red pixels and get count of number of red pixels
    # mask = cv2.inRange(frame, lower_red, upper_red, axis=2)
    # num_red_px = cv2.countNonZero(mask)
    # cv2.imshow("Mask", mask)
    # cv2.imshow("Mask", cv2.bitwise_and(frame, frame, mask=mask))
    # cv2.imshow("mask", mask)
    return num_red_px




''' CAMERA WORK '''

video = cv2.VideoCapture(0)
video.set(cv2.CAP_PROP_FRAME_WIDTH,320)
video.set(cv2.CAP_PROP_FRAME_HEIGHT,240)

time.sleep(2)


''' CONSTANTS (for PD algorithm) '''

speed = 8 
lastTime = 0
lastError = 0


pwm = PWMControl()


''' BEGIN MAIN CODE '''

# Set up signal handler so ctrl+c triggers the handler
# This means the shutdown code will actually run
done = False

# TODO: set initial speed
# pwm.set_throttle(int(65535 / 1.9))


def stop(signum, stackframe):
    global done
    done = True

signal.signal(signal.SIGINT, stop)

show_camera = True 



''' SETTING P AND D VALUES '''

kp = 0.2    # change for testing purposes
kd = kp * 0.1

stop_timing = 0
stop_state = 0




''' PLOTTING DATA '''

error_data = []
steering_pwm_data = []
throttle_pwm_data = []
proportional_resp_data = []
derivative_resp_data = []



''' MAIN FUNCTION '''
num_stopped = 0

while not done:
    ret,frame = video.read()

    # Detect lanes
    edges = detect_edges(frame)
    roi = region_of_interest(edges)
    line_segments = detect_line_segments(roi)
    lane_lines = average_slope_intercept(frame,line_segments)
    lane_lines_image = display_lines(frame,lane_lines)
    steering_angle = get_steering_angle(frame, lane_lines)
    heading_image = display_heading_line(lane_lines_image,steering_angle)

    if show_camera:
        cv2.imshow("heading line",heading_image)

    # Stop sign detection (x2)
    red_px = check_for_stop_sign(frame)
    print(f"{red_px=}")
    print(f"{stop_state=}")

    # TODO: adjust values of picture detection
    # Need this to stop twice
    if red_px > 20000:
        num_stopped += 1
        print(f'Stopping! {num_stopped}')
        break


    ''' CALCULATE DERIVATIVE FROM PD ALGORITHM '''
    now = time.time()
    dt = now - lastTime
    deviation = steering_angle - 90

    error = -deviation
    base_turn = 7.5
    proportional = kp * error
    derivative = kd * (error - lastError) / dt

    error_data.append(error)
    proportional_resp_data.append(proportional)
    derivative_resp_data.append(derivative)


    ''' DETERMINE TURN AMOUNT (WITH PWM CONTROL) '''
    turn_amt: int = base_turn + proportional + derivative
    print(f"Steering angle: {steering_angle}")
    print(f"Turn amt: {turn_amt}")

    if turn_amt < 6:
        turn_amt = int(65535 / 2.5)
    elif turn_amt > 9:
        turn_amt = int(65535 / 1.5)
    

    #print(f"Turn amt: {turn_amt}")
    #steering_pwm_data.append(pwm.set_steering(turn_amt))

    lastError = error
    lastTime = time.time()

    key = cv2.waitKey(1)
    if key == 27:
        break


''' SHUTDOWN PROTOCOL '''

video.release()
pwm.shutdown()

with open("data.py", 'w') as data:
    data.write(f"{error_data=}")
    data.write("\n")
    data.write(f"{throttle_pwm_data=}")
    data.write("\n")
    data.write(f"{steering_pwm_data=}")
    data.write("\n")
    data.write(f"{proportional_resp_data=}")
    data.write("\n")
    data.write(f"{derivative_resp_data=}")
