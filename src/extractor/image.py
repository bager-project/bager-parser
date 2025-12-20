# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: image extractor

import cv2
import numpy as np
import os
from shapely.geometry import LineString, Polygon

class Image:
    """
        Extract entities from an image and convert them into Shapely elements.
        
        :param str path: path to the image file
        :param bool debug: is debug mode on
        :param bool flip_y: should we flip by Y axis
        :param float simplify_tolerance: threshold value controlling the level of simplification
        :param bool remove_colinear: do you want to remove colinear points in a polygon
    """

    def __init__(self, path, debug, flip_y, simplify_tolerance, remove_colinear):
        """
            Initialize variables.
        """

        self.path = path
        self.elements = []

        if not os.path.exists(path):
            print(f"[EXTRACTOR-IMAGE] File in path '{path}' does not exist!")
            print("[EXTRACTOR-IMAGE] Exiting...")

            exit(0)

        self.debug = debug

        self.flip_y = flip_y
        self.simplify_tolerance = simplify_tolerance
        self.remove_colinear = remove_colinear

    def execute(self):
        """
            Extract.
        """

        self.extract_entities()

    ###########################################################################
    #####                                                                 #####
    ###########################################################################

    def extract_entities(self):
        """
            Extract entities from an image and convert them to Shapely geometry.
        """

        #########################################
        # Parameters
        #########################################

        THRESHOLD_VALUE = 200
        MIN_CONTOUR_AREA = 30
        MORPH_KERNEL_SIZE = 3

        #########################################
        # Load image
        #########################################

        image = cv2.imread(self.path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise IOError("[EXTRACTOR-IMAGE] Image has not been found!")
        
        height, width = image.shape[:2]

        #########################################
        # Binary threshold
        # Black lines on white background
        #########################################

        _, binary = cv2.threshold(
            image,
            THRESHOLD_VALUE,
            255,
            cv2.THRESH_BINARY_INV
        )

        #########################################
        # Morphological cleanup
        # (connect broken lines)
        #########################################

        kernel = np.ones((MORPH_KERNEL_SIZE, MORPH_KERNEL_SIZE), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        #########################################
        # Find contours (vector extraction)
        #########################################

        contours, _ = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_NONE
        )

        #########################################
        # Convert to Shapely geometry
        #########################################

        self.contours_to_shapely(
            contours,
            height,
            MIN_CONTOUR_AREA
        )

        #########################################
        # Visualization
        #########################################
        if self.debug == True:
            self.visualize(image, binary, contours, MIN_CONTOUR_AREA)
    
    def get_elements(self):
        """
            Return Shapely elements.
        """

        return self.elements
    
    ###########################################################################
    #####                                                                 #####
    ###########################################################################
    
    def contours_to_shapely(self, contours, image_height, min_area=0):
        """
            INTERNAL FUNCTION!

            Convert OpenCV contours to the Shapely geometry.
        """

        for cnt in contours:
            if cv2.contourArea(cnt) < min_area:
                continue

            coords = cnt.reshape(-1, 2)

            # Detect closed contour
            if np.linalg.norm(coords[0] - coords[-1]) <= 2:

                if self.remove_colinear:
                    geom = Polygon(self.remove_collinear_2d(coords))
                
                else:
                    geom = Polygon(coords)

            else:
                geom = LineString(coords)

            if self.flip_y == True:
                geom = self.flip_y_function(geom, image_height)

            if self.simplify_tolerance > 0:
                geom = geom.simplify(self.simplify_tolerance, preserve_topology=True)

            self.elements.append(geom)

    def flip_y_function(self, geom, height):
        """
            INTERNAL FUNCTION!

            Flip an element by 180 degrees on Y axis.
        """

        if isinstance(geom, Polygon):
            # Flip exterior ring
            exterior = [(x, height - y) for x, y in geom.exterior.coords]

            # Flip interior rings (holes)
            interiors = [
                [(x, height - y) for x, y in interior.coords]
                for interior in geom.interiors
            ]

            return Polygon(exterior, interiors)

        elif isinstance(geom, LineString):
            return LineString([(x, height - y) for x, y in geom.coords])

        else:
            raise TypeError(f"[EXTRACTOR-IMAGE] Unsupported geometry type: {type(geom)}")

    def remove_collinear_2d(self, coords):
        """
            INTERNAL FUNCTION!

            Remove collinear points from a 2D polygon.
        """

        if len(coords) < 3:
            return coords

        simplified = [coords[0]]
        
        for i in range(1, len(coords) - 1):
            x1, y1 = simplified[-1]
            x2, y2 = coords[i]
            x3, y3 = coords[i+1]

            # Check if points are collinear
            if (y2 - y1)*(x3 - x2) != (y3 - y2)*(x2 - x1):
                simplified.append(coords[i])

        simplified.append(coords[-1])
        return simplified

    ###########################################################################
    #####                                                                 #####
    ###########################################################################

    def visualize(self, image, binary, contours, MIN_CONTOUR_AREA):
        """
            DEBUG FUNCTION!

            Show detected lines.
        """

        vis = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        valid_contours = []
        for cnt in contours:
            if cv2.contourArea(cnt) >= MIN_CONTOUR_AREA:
                valid_contours.append(cnt)
                cv2.drawContours(vis, [cnt], -1, (0, 255, 0), 1)

        print(f"[EXTRACTOR-IMAGE-DEBUG] Detected contours: {len(valid_contours)}")

        cv2.imshow("Binary", binary)
        cv2.imshow("Detected Lines", vis)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
