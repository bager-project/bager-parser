# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Positioner

import cv2
import numpy as np
import os
from shapely.geometry import Point, LineString
import toml

class Positioner:
    """
        Transform coordinates of polygons and divisions into a set
        of coordinates from `position.toml` file.

        Attributes:
            path(str): path to the `position.toml` file
            polygons(list): list of polygons
            divisions(list): list of lines (divisions) FOR EACH polygon
    """

    def __init__(self, path, polygons, divisions):
        """
            Initialize all the variables.
        """

        self.path = path
        if not os.path.exists(path):
            print(f"File in path '{path}' does not exist!")
            print("Exiting...")

            exit(0)

        self.polygons = polygons
        self.divisions = divisions

        # Array holding new points for each polygon
        self.transformed_polygons_coords = []

        # Array holding new LineStrings for each division of each polygon
        self.transformed_divisions_coords = []
    
    def execute(self):
        """
            Transform positions.
        """

        parsed_toml = toml.load(self.path)
        polygon_coords = parsed_toml['gps']['polygon_coords']
        divisions_coords = parsed_toml['gps']['division_coords']

        for i in range(len(self.polygons)):
            transformed = self.transform_polygon_coords(self.polygons[i].exterior.coords, polygon_coords[i])
            self.transformed_polygons_coords.append(transformed)

            transformed_lines = self.transform_divisions_coords(self.divisions[i], divisions_coords[i])
            self.transformed_divisions_coords.append(transformed_lines)

    def transform_polygon_coords(self, shapely_coords, toml_coords):
        """
            Transform coordinates of a given polygon.
            Return a list of Points.
        """

        n_toml = len(toml_coords)
        n_shapely = len(shapely_coords)

        if n_toml < 3:
            raise ValueError("OpenCV affine transform requires at least 3 points")

        if n_toml > n_shapely:
            raise ValueError("More TOML points than Shapely points is unsupported")

        # Use first n_toml points from shapely as source, convert to float32 for OpenCV
        src = np.array(shapely_coords[:n_toml], dtype=np.float32)
        dst = np.array(toml_coords, dtype=np.float32)

        # If exactly 3 points: use getAffineTransform (3x2 inputs)
        if n_toml == 3:
            M = cv2.getAffineTransform(src, dst)  # 2x3 matrix
        else:
            # For more than 3 points, use estimateAffinePartial2D (robust affine)
            M, inliers = cv2.estimateAffinePartial2D(src, dst)
            if M is None:
                raise RuntimeError("Failed to estimate affine transform")

        # Apply affine transform matrix M to all shapely points
        transformed = []
        for p in shapely_coords:
            point = np.array([p[0], p[1], 1.0])  # homogeneous coordinate
            x, y = M.dot(point)
            transformed.append(Point(x, y))

        return transformed

    def transform_divisions_coords(self, linestrings, toml_start_points):
        """
            Transform coordinates of a given LineStrings array.
            Return new LineStrings.
        """

        transformed_lines = []

        for line, toml_start in zip(linestrings, toml_start_points):
            shapely_coords = np.array(line.coords, dtype=np.float32)
            
            # Calculate translation vector:
            # Move shapely start point to toml_start
            offset = np.array(toml_start) - shapely_coords[0]

            # Translate all points by offset
            transformed_coords = shapely_coords + offset

            transformed_lines.append(LineString(transformed_coords))

        return transformed_lines
