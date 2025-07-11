# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Positioner

import cv2
import numpy as np
import os
from shapely import affinity
from shapely.geometry import Polygon
import toml

class Positioner:
    """
        Transform coordinates of polygons and divisions into a set
        of coordinates from `position.toml` file.

        Attributes:
            path(str): path to the `position.toml` file
            depth_array(str): list defining depth for each polygon
            polygons(list): list of polygons
            divisions(list): list of lines (divisions) FOR EACH polygon
    """

    def __init__(self, path, depth_array, polygons, divisions):
        """
            Initialize all the variables.
        """

        self.path = path
        self.depth_array = depth_array

        self.polygons = polygons
        self.divisions = divisions

        self.transformed_polygons = []
        self.transformed_divisions = []

    def execute(self):
        """
            Transform positions.
        """

        if os.path.exists(self.path):
            parsed_toml = toml.load(self.path)
            polygon_coords = parsed_toml['gps']['polygon_coords']

            for i, polygon in enumerate(self.polygons):
                new_poly_coords = polygon_coords[i]
                transformed_poly, affine_matrix = self.transform_polygon(polygon, new_poly_coords)
                self.transformed_polygons.append(transformed_poly)

                transformed_divs = self.transform_divisions(self.divisions[i], affine_matrix)
                self.transformed_divisions.append(transformed_divs)

        else:
            self.transformed_polygons = self.polygons
            self.transformed_divisions = self.divisions

        # Add depth
        for i, poly in enumerate(self.transformed_polygons):
            transformed_poly = Polygon([(x, y, self.depth_array[i]) for x, y in poly.exterior.coords])
            self.transformed_polygons[i] = transformed_poly

    def get_elements(self):
        """
            Return polygons and their divisions in transformed shape.
        """

        return (self.transformed_polygons, self.transformed_divisions)

    ###########################################################################
    #####                                                                 #####
    ###########################################################################

    def transform_divisions(self, lines, M):
        """
            INTERNAL FUNCTION!

            Transform divisions of the polygon using same affine matrix in
            polygon transformation.
        """

        a, b, tx = M[0]
        d, e, ty = M[1]
        affine_params = [a, b, d, e, tx, ty]

        return [affinity.affine_transform(line, affine_params) for line in lines]

    def transform_polygon(self, polygon, toml_coords):
        """
            INTERNAL FUNCTION!

            Transform polygon coordinates using affine transformation.
        """

        shapely_coords = list(polygon.exterior.coords)
        n_src = len(shapely_coords)
        n_dst = len(toml_coords)

        if n_dst < 3:
            raise ValueError("At least 3 points are required for affine transform.")

        if n_dst > n_src:
            raise ValueError("TOML polygon has more points than source polygon.")

        src = np.array(shapely_coords[:n_dst], dtype=np.float32)
        dst = np.array(toml_coords, dtype=np.float32)

        if n_dst == 3:
            M = cv2.getAffineTransform(src, dst)
        else:
            M, inliers = cv2.estimateAffinePartial2D(src, dst)
            if M is None:
                raise RuntimeError("Affine transform could not be estimated.")

        # Convert OpenCV 2x3 matrix to Shapely-compatible flat list
        a, b, tx = M[0]
        d, e, ty = M[1]
        affine_params = [a, b, d, e, tx, ty]

        transformed = affinity.affine_transform(polygon, affine_params)
        return transformed, M
