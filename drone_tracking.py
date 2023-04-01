# Directions for use:
# • [Space]: Stop – set all directional and rotational velocities to 0.
# • [T]: Track – engage face tracking mode
# • [Up] and [Down] arrow keys: Move forward or backward respectively
# (x-axis).
# • [Left] and [Right] arrow keys: Move left or right respectively (y-axis).
# • [K]: Upward. (z-axis)
# • [L]: Downward: (z-axis)
# • [,] (<) and [.] (>): Rotate left or right respectively (yaw).
# • [Q]: Emergency stop – Lands if the drone is flying. Terminates program.
# • [B]: Prints battery status to the terminal.

# Tracking disengages if any other input is given

import cv2 as cv
from pynput.keyboard import Key, Listener
from threading import Thread
from djitellopy import Tello

#   #   #   #   #   #   #

#       FUNCTIONS       #

def get_face(image):
    haar_cascade = cv.CascadeClassifier('haar_face.xml')
    return haar_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=quality)


def get_adjustments(coordinates, box_width):
    adjustments = [0, 0, 0]

    if coordinates[0] > width * (3 / 5):  # RIGHT
        adjustments[0] = 1
    if coordinates[0] < width * 2 / 5:  # LEFT
        adjustments[0] = -1
    if box_width > 250:  # BACK
        adjustments[1] = -1
    if box_width < 150:  # FORWARD
        adjustments[1] = 1
    if coordinates[1] < height * (3 / 7):  # DOWN
        adjustments[2] = 1
    if coordinates[1] > height * (4 / 7):  # UP
        adjustments[2] = -1

    return adjustments


def adjust(tello, adjustments):
    try:
        left_right = adjustments[4]
    except:
        left_right = 0

    tello.send_rc_control(speed * left_right, speed * adjustments[1], speed * adjustments[2],
                          speed * adjustments[0])  # z is inverted because y-axis is
    # inverted


def key_input():
    def on_press(key):
        if valid_inputs.__contains__(key):
            if not input_buffer.__contains__(key):
                global input_buffer
                input_buffer.insert(key)

    def on_release(key):
        global input_buffer
        input_buffer.remove(key)

        global track
        if key == 't':
            track = True
        else:  # Disengage tracking if any other button is pressed
            track = False

    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()


#   CONTROL VARIABLES   #

takeoff = False
streaming = True
track = False
quality = 17
width = 960
height = 720
speed = 30
valid_inputs = [Key.left, Key.right, Key.up, Key.down, Key.space, 't', 'k', 'l', ',', '.', 'b']
input_buffer = []


#   #   #   #   #   #   #
# Connecting

drone = Tello()
drone.connect()

print(drone.get_battery())

# Takeoff

if takeoff:
    drone.takeoff()
    takeoff = False

# Start stream
if streaming:
    drone.streamoff()
    drone.streamon()

# writing to file
result = cv.VideoWriter('Drone_feed.avi',
                        cv.VideoWriter_fourcc(*'MJPG'),
                        10, (width, height))

th = Thread(target=key_input)   # separate thread for keyboard inputs
th.start()

while streaming:
    feed = drone.get_frame_read()
    frame = feed.frame
    frame = cv.resize(frame, (width, height))
    result.write(frame)

    # Haar Cascade
    faces_rect = get_face(frame)

    position = [0, 0, 0]
    for (x, y, w, h) in faces_rect:
        cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), thickness=2)   # drawing bounding box for face
        center = (x + round(w / 2), y + round(h / 2))
        cv.rectangle(frame, center, center, (225, 0, 0), thickness=5)  # centre of face

        position = get_adjustments(center, w)

        lr = 'left' if position[0] < 0 else 'right' if position[0] > 0 else 'centre'
        bf = 'close' if position[1] < 0 else 'far' if position[1] > 0 else 'centre'
        ud = 'low' if position[2] < 0 else 'high' if position[2] > 0 else 'centre'

        text = f'Position: ({lr}, {bf}, {ud})'
        text1 = f'Position: ({center[0]}, {center[1]})'

        cv.putText(frame, str(text), (x, y + h + 15), cv.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), thickness=1)

    cv.imshow('Drone Feed', frame)

    if track:   # If tracking is on, use adjustments based on face detection
        adjust(drone, position)
    else:  # adjust according to key inputs
        cmd = [0, 0, 0, 0]  # [forward-backward, up-down, rotate left-right, move left-right]

        if input_buffer.__contains__(Key.down):     # move backward
            cmd[2] = -1
        if input_buffer.__contains__(Key.up):       # move forward
            cmd[2] = 1
        if input_buffer.__contains__('l'):          # move down
            cmd[2] = -1
        if input_buffer.__contains__('k'):          # move up
            cmd[2] = 1
        if input_buffer.__contains__(','):          # rotate left
            cmd[3] = -1
        if input_buffer.__contains__('.'):          # rotate right
            cmd[3] = 1
        if input_buffer.__contains__(Key.left):     # move left
            cmd[4] = -1
        if input_buffer.__contains__(Key.right):    # move right
            cmd[4] = 1
        if input_buffer.__contains__('b'):          # display battery %
            cmd[4] = 1
        if input_buffer.__contains__(Key.space):    # clear all inputs
            cmd = [0, 0, 0, 0]

        adjust(drone, cmd)


result.release()
drone.streamoff()
th.join()
cv.destroyAllWindows()
