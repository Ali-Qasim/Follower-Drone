# Follower-Drone

This technical documentation describes the structure and function of drone_tracking.py.

drone_tracking.py is a Python script written for Python 3.8.6, to implement face-tracking and
following using the DJI Tello drone. The libraries used are cv2 (from opencv-python) and Tello (from
djitellopy). It was also planned to integrate the use of the RoboMaster attachments for DJI Tello for
indoor mapping and frontal proximity sensing, however, the lack of English language documentation
for the robomaster library made this unfeasible. The script allows the user to manually control the DJI
Tello drone or enable autonomous following. The drone can then use its camera feed to identify a face
and follow it. A multi-threaded approach was used so that input/output operations do not interrupt
each other where undesirable.

Hardware
drone_tracking.py is designed to run on the base DJI Tello and has been tested on Tello EDU and RM
TT models also. The addition of a GPS sensor was planned for use with the RM TT attachment’s
GPIO pins but could not be integrated into this project.
The DJI Tello drone was chosen as it is a low-cost, easily accessible, small-and-light drone, which
makes it perfect for this project. The Mavic Mini was also considered since this has an onboard GPS
but is more than double the price of the Tello, so it was excluded. The RM TT is also similarly
expensive, but as it is simply a higher spec version of the Tello, it can be considered an optional
upgrade.

Software
drone_tracking.py is designed for use with Python 3.8.6. It was originally written for Python 3.10, as
it has newly added match-case support. This was not suitable, however, as the imports required for
this project do not currently have Python 3.10 compatibility. The IDE used for development was
JetBrains PyCharm 2021.3.2.
Libraries imported were:
• cv2 from opencv-python
• Tello from djitellopy
• keyboard

Structure
This code was written with reference to programs written by Murtaza Hassan.
The script is divided into 4 sections:
1. Imports, as described above

2. Control Variables:
a. takeoff: Boolean controlling whether take-off is allowed or not
b. streaming: Boolean controlling if the drone’s camera feed is streamed.
c. track: Boolean controlling on/off state of autonomous tracking.
d. quality: Integer value controlling leniency of face detection algorithm (lower quality
means less strict judgement of faces and more noise. Higher quality means faces are
detected more selectively but can result in no matches found if too low)
e. width and height: Set the dimensions of the window for displaying the drone stream.

3. Function Definitions:
a. key_input(): Function defining key input functionality to allow the user to operate
drone using the keyboard. This was initially implemented using a match-case block in
python (similar to switch-case in most other languages, recently implemented in
python 3.10) but had to be rewritten when the project was switched to python 3.8 due
to compatibility issues mentioned in the Software section above.
Initially, the function was written so the drone was sent commands directly from the
input function using Tello.send_rc_control(y, x, z, yaw), however, this interrupted the
main thread hence interrupting the video stream. This approach was also using
cv.waitKeyEx() which would not allow multi-key input to enable diagonal (2+ x, y, z
directions) or arcing (displacement+rotation) movement.
Key inputs are read on a separate thread and stored in an array while pressed to
remedy these problems. When a key is released, it is purged from the array. All the
keys currently stored in the array are then used to send the movement command to the
drone.
The key commands are as follows:
• [Space]: Stop – set all directional and rotational velocities to 0.
• [T]: Track – engage face tracking mode
• [Up] and [Down] arrow keys: Move forward or backward respectively
(x-axis).
• [Left] and [Right] arrow keys: Move left or right respectively (y-axis).  
• [K]: Upward. (z-axis)
• [L]: Downward: (z-axis)
• [,] (<) and [.] (>): Rotate left or right respectively (yaw).
• [Q]: Emergency stop – Lands if the drone is flying. Terminates program.
• [B]: Prints battery status to the terminal.
If any button other than [T] is pressed, the track variable is set to false and the
drone re-enters manual control mode.
b. get_adjustments(): Function which returns adjustments[y, z, yaw], an array describing
the necessary adjustments to centre the target in frame.
This is done by:
• If the bounding rectangle of the face is too large, move backwards. If too
small, move forward. y=1 indicates forward movement while y=-1 indicates
backward movement.
• If the bounding rectangle is too far left, rotate left. If too far right, rotate right.
yaw=-1 indicates rotation left, while yaw=1 indicates rotation right.
• If the bounding rectangle is too far down, move upward. If too far up, move
downward. z=1 indicates movement up, while z=-1 indicates movement
down.
adjustments[] is an array containing a combination of all operations needed to
maintain the centring of the target in frame. Jabril also uses a similar frame-position
based approach to determine adjustments required in his video series.
c. adjust(): Function which uses the array of adjustments, adjustments[], from
get_adjustments() and sends commands to the drone to perform corrective
manoeuvres.
This was originally written using the Tello.move() functions, but these interrupt the
main thread as they wait for movement confirmation before allowing the thread to
resume. The Tello.send_rc_control() function simply sends a command to set
directional and rotational velocities, and so is suitable for use in the main thread.
d. get_face(): Function which returns the coordinates and dimensions of the bounding
box of a detected face for each frame of the drone feed. It utilises the Viola-jones
object-detection algorithm (VJA) using a pre-trained Haar feature-based cascade classifier. This project did not endeavour to train a novel classifier. The VJA cannot
differentiate faces from other faces, so training a user-specific classifier for individual
facial recognition would not have been of merit. The VJA requires frontal, upright
faces, so this works well for a face-following drone, however, this approach could be
improved in both computational performance and robustness by implementing other
algorithms in conjunction with VJA.

4. Initialisation and start-up: Connect to drone and begins initial take-off. Start the container
loop for the drone’s video stream and user interface.


Face Recognition:
Face recognition for this project was carried out using the VJA, as discussed in previous sections.
VJA is an object detection algorithm proposed in 2001 by Paul Viola and Michael Jones. The
algorithm has four stages:
Haar feature selection:
The algorithm uses the Haar features shown below to extract features from the dataset of training
images. Each feature is a single value obtained by subtracting the sum of pixels under the white
rectangles from the pixels under the dark rectangles, much like the convolutional matrices used to
apply masks. All configurations of dimension and position are used to calculate features for each
image.

Adaboost:
The algorithm then finds the features which yield a minimum error rate (most positives and least
negatives). The final classifier is a weighted sum of these ‘weak’ classifiers.
Cascaded Classifiers:
Even after the Adaboost stage, the final classifier consists of many thousands of features. Applying
all these features to each image would be superfluous and computationally expensive. To combat this,
the features are cascaded – features are grouped into stages to be applied successively. Images are
only tested against the features in stage 2 after passing 1, and so on. This approach greatly optimises
the computational power expended on non-matching images.
