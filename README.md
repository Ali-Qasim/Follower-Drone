# Follower-Drone

This is a Python app I created for the DJI Tello to allow it to follow a user by tracking their face!

![image](https://user-images.githubusercontent.com/67727388/229280738-79246398-5f67-4b49-8031-94537e46cf47.png)

Key Inputs:

The key commands are as follows:
• [Space]: Stop – set all directional and rotational velocities to 0.
• [T]: Track – Engage face tracking mode
• [Up] and [Down] arrow keys: Move forward or backward respectively (x-axis).
• [Left] and [Right] arrow keys: Move left or right respectively (y-axis).
• [K]: Upward. (z-axis) • [L]: Downward: (z-axis)
• [,] (<) and [.] (>): Rotate left or right respectively (yaw).
• [Q]: Emergency stop – Stops rotors and drone drops. Terminates program.
• [B]: Prints battery status to the terminal.

If any button other than [T] is pressed, the track variable is set to false and the drone re-enters manual control mode. 

For more details, refer to tech-doc.txt
