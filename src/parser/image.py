# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: 
# DESCRIPTION: image parser entry file

import os
import cv2
import numpy as np

class Image:

    # Initialize all variables
    def __init__(self, path) -> None:

        if not os.path.exists(path):
            print(f"File in path {path} does not exist!")
            print("Exiting...")

            exit(0)

        self.image = cv2.imread(path)

    def execute(self) -> None:
        # Convert image to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        # Use canny edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Apply HoughLinesP method to 
        # to directly obtain line end points
        lines_list =[]
        lines = cv2.HoughLinesP (
                    edges,                  # Input edge image
                    1,                      # Distance resolution in pixels
                    np.pi / 180,            # Angle resolution in radians
                    threshold = 100,        # Min number of votes for valid line
                    minLineLength = 5,      # Min allowed length of line
                    maxLineGap = 10         # Max allowed gap between line for joining them
                )

        # Iterate over points
        for points in lines:
            # Extracted points nested in the list
            x1, y1, x2, y2 = points[0]

            # Draw the lines joining the points
            # On the original image
            cv2.line(self.image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Maintain a simples lookup list for points
            lines_list.append([(x1, y1),(x2, y2)])
            
        # Save the result image
        cv2.imwrite('detectedLines.png', self.image)
