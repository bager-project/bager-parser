# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Positioner

import numpy as np
from shapely import affinity
from shapely.geometry import Polygon

class Positioner:
    """
        Transform coordinates of polygons and divisions into a set
        of coordinates from `position.toml` file.

        Attributes:
            coords(list): list of new coordinates
            depth_array(str): list defining depth for each polygon
            scale(float): scale coefficient for all polygons
            polygons(list): list of polygons
            divisions(list): list of lines (divisions) FOR EACH polygon
    """

    def __init__(self, coords, depth_array, scale, polygons, divisions):
        """
            Initialize all the variables.
        """

        self.coords = coords
        self.depth_array = depth_array
        self.scale = scale

        self.polygons = polygons
        self.divisions = divisions

        self.transformed_polygons = []
        self.transformed_divisions = []

    def execute(self):
        """
            Transform polygons.
        """
        
        #########################################
        # Transform positions
        #########################################

        if len(self.coords) == len(self.polygons):
            for i, polygon in enumerate(self.polygons):
                transformed_poly, affine_matrix = self.transform_polygon(polygon, self.coords[i])
                self.transformed_polygons.append(transformed_poly)

                transformed_divs = self.transform_divisions(self.divisions[i], affine_matrix)
                self.transformed_divisions.append(transformed_divs)

        else:
            self.transformed_polygons = self.polygons
            self.transformed_divisions = self.divisions

            # If array length is zero, we assume user intentionally
            # does not want to change coordinates and we do not
            # need to print an error message
            if len(self.coords) > 0:
                print("[POSITIONER] Length of `coords` array does not match" +
                      "number of polygons! Ignoring coordinates" +
                      "transformation process.")

        #########################################
        # Scale
        #########################################

        if self.scale == 0.0:
            self.scale = 1.0

        self.transformed_polygons = [
            affinity.scale(poly, xfact=self.scale, yfact=self.scale, origin=(0, 0))
            for poly in self.transformed_polygons
        ]

        self.transformed_divisions = [
            [
                affinity.scale(line, xfact=self.scale, yfact=self.scale, origin=(0, 0))
                for line in division
            ]
            for division in self.transformed_divisions
        ]

        #########################################
        # Add depth
        #########################################

        if len(self.depth_array) != len(self.transformed_polygons):
            # If array length is zero, we assume user intentionally 
            # does not want to change depth and we do not need to
            # print an error message
            if len(self.depth_array) > 0:
                print("[POSITIONER] Length of `depth` array does not match" +
                      "number of polygons! Defaulting depth for all" +
                      "polygons to zero.")

            self.depth_array = []
            for i in range(len(self.transformed_polygons)):
                self.depth_array.append(0)

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

            Transform divisions of the polygon using the same affine matrix
            used in polygon transformation.
        """

        a, b, tx = M[0]
        d, e, ty = M[1]
        affine_params = [a, b, d, e, tx, ty]

        return [affinity.affine_transform(line, affine_params) for line in lines]

    def transform_polygon(self, polygon, toml_coords, int_tol=1e-4, dec_places=6):
        """
            INTERNAL FUNCTION!

            Transform polygon coordinates using affine transformation.
        """

        src_coords = list(polygon.exterior.coords)
        n_src = len(src_coords)
        n_dst = len(toml_coords)

        if n_dst < 3:
            raise ValueError("[POSITIONER] At least 3 points are required" +
                             "for an affine transform.")

        if n_dst > n_src:
            raise ValueError("[POSITIONER] TOML polygon has more points" +
                             "than the source polygon.")

        src = np.asarray(src_coords[:n_dst], dtype=float)
        dst = np.asarray(toml_coords, dtype=float)

        # Build A·p = b
        A = np.zeros((2 * n_dst, 6))
        b = np.zeros( 2 * n_dst)

        A[0::2, 0] = src[:, 0]   # a * x
        A[0::2, 1] = src[:, 1]   # b * y
        A[0::2, 4] = 1           # tx
        b[0::2]   = dst[:, 0]

        A[1::2, 2] = src[:, 0]   # d * x
        A[1::2, 3] = src[:, 1]   # e * y
        A[1::2, 5] = 1           # ty
        b[1::2]   = dst[:, 1]

        # Least‑squares solve
        p, *_ = np.linalg.lstsq(A, b, rcond=None)
        if np.linalg.matrix_rank(A) < 6:
            raise RuntimeError("[POSITIONER] Control points are degenerate;" +
                               "rank-deficient system.")

        # Round numbers if they are within the tolerance range
        for i, coef in enumerate(p):
            nearest_int = np.round(coef)
            if abs(coef - nearest_int) <= int_tol:
                p[i] = nearest_int
            else:
                p[i] = np.round(coef, dec_places)

        a, b_, d, e, tx, ty = p
        M = np.array([[a, b_, tx],
                    [d, e, ty]], dtype=float)

        transformed = affinity.affine_transform(polygon, [a, b_, d, e, tx, ty])
        return transformed, M
