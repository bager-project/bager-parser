# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Image extractor entry file

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

        self._color_gradation = False
        self._two_color_gradation = False

        # Dictionary to store all elements
        # https://ezdxf.readthedocs.io/en/stable/dxfentities/index.html
        self.elements = {
            'ARC': [],
            'ATTRIB': [],
            'BODY': [],
            'CIRCLE': [],
            'DIMENSION': [],
            'ARC_DIMENSION': [],
            'ELLIPSE': [],
            'HATCH': [],
            'HELIX': [],
            'IMAGE': [],
            'INSERT': [],
            'LEADER': [],
            'LINE': [],
            'LWPOLYLINE': [],
            'MLINE': [],
            'MESH': [],
            'MPOLYGON': [],
            'MTEXT': [],
            'MULTILEADER': [],
            'POINT': [],
            'POINTS': [], # this is for image extractor
            'POLYLINE': [],
            'VERTEX': [],
            'RAY': [],
            'REGION': [],
            'SHAPE': [],
            'SOLID': [],
            'SPLINE': [],
            'SURFACE': [],
            'TEXT': [],
            'TRACE': [],
            'VIEWPORT': [],
            'WIPEOUT': [],
            'XLINE': [],
            'UNIMPLEMENTED': [],
        }

    def color_gradation(self, line_length, min_length, max_length):
        # Normalize the length to the range [0, 1]
        norm_length = (line_length - min_length) / (max_length - min_length)

        # Light red to Dark red gradient
        red_intensity = int(139 + norm_length * (255 - 139))  # Darker red for thicker lines
        color = (0, 0, red_intensity)  # BGR format: (Blue, Green, Red)

        # Set line thickness based on normalized length (optional)
        thickness = int(1 + norm_length * 5)  # Range from 1 to 5

        return (color, thickness)
    
    def two_color_gradation(self, line_length, min_length, max_length):
        # Normalize the length to the range [0, 1]
        norm_length = (line_length - min_length) / (max_length - min_length)

        # Green to Red gradient
        # Green (0, 255, 0) -> Red (0, 0, 255)
        red_value = int(norm_length * 255)   # Red increases as line gets thinner
        green_value = int(255 - norm_length * 255)  # Green decreases as line gets thinner
        color = (0, green_value, red_value)  # BGR format: Blue, Green, Red

        # Set line thickness based on normalized length (optional)
        thickness = int(1 + norm_length * 5)  # Range from 1 to 5

        return (color, thickness)
    
    def no_gradation(self, line_length, length_threshold):
        # Use two colors based on length threshold
        if line_length >= length_threshold:
            color = (0, 255, 0)  # Green for thicker lines
            thickness = 4  # Thicker line

        else:
            color = (0, 0, 255)  # Red for thinner lines
            thickness = 2  # Thinner lines

        return (color, thickness)

    def execute(self) -> None:
        # Convert image to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        # Use Canny edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Apply HoughLinesP method to directly obtain line end points
        lines = cv2.HoughLinesP(
            edges,                      # Input edge image
            1000,                       # Distance resolution in pixels
            np.pi / 180,                # Angle resolution in radians
            threshold=1,                # Min number of votes for valid line
            minLineLength=1,            # Min allowed length of line
            maxLineGap=1                # Max allowed gap between lines for joining them
        )

        if lines is not None:
            # Calculate the maximum and minimum line lengths
            line_lengths = [np.sqrt((x2 - x1)**2 + (y2 - y1)**2) for [[x1, y1, x2, y2]] in lines]
            max_length = max(line_lengths)
            min_length = min(line_lengths)

            # Define a threshold to classify thick vs thin lines
            length_threshold = (max_length + min_length) / 2

            # Iterate over detected lines
            for i, points in enumerate(lines):
                # Extracted points
                x1, y1, x2, y2 = points[0]

                self.elements['POINTS'].append((x1, y1))
                self.elements['POINTS'].append((x2, y2))

                # Calculate the length of the line
                line_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

                color = 0
                thickness = 0

                if self._color_gradation:
                    if self._two_color_gradation:
                        result = self.two_color_gradation(line_length, min_length, max_length)

                        color = result[0]
                        thickness = result[1]

                    else:
                        result = self.color_gradation(line_length, min_length, max_length)

                        color = result[0]
                        thickness = result[1]
                else:
                    result = self.no_gradation(line_length, length_threshold)

                    color = result[0]
                    thickness = result[1]

                # Draw the lines on the image
                cv2.line(self.image, (x1, y1), (x2, y2), color, thickness)

        # Save the result image
        cv2.imwrite('detectedLines.png', self.image)

    def get_elements(self):
        return self.elements
