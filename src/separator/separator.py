# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Separator

import colorama
import math
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Point, Polygon
from shapely.ops import linemerge, polygonize, snap

class Separator:
    """
        Create a polygon from Shapely elements
        and divide them into smaller divisions/cells.

        Attributes:
            elements(list): Shapely elements
    """

    def __init__(self, elements):
        """
            Initialize all the variables.
        """

        self.elements = elements

        # Are we in debug mode
        self.debug = False

        # Variable holding polygons/shapes
        self.polygons = []

        # Variable holding divisions for each polygon
        self.divisions = []

        # Variable holding grid size
        self.grid_size = 25

        # Variable holding minimal spacing in curved segments
        self.min_spacing = 10.0

        self.create_polygons()

        if len(self.polygons) != 0:
            self.create_divisions()

    def create_polygons(self):
        """
            Create a polygon from Shapely elements.
        """

        start_point = None
        elements_array = []
        coords_array = []

        if self.debug == True:
            print(f"Extracted Shapely elements: \n{self.elements}.\n")

        for element in self.elements:
            match element:
                case LineString():
                    if self.debug == True:
                        if start_point != None:
                            print(colorama.Fore.LIGHTCYAN_EX + f"Reference: {Point(start_point)}" + colorama.Fore.RESET)
                        print(f"Start point: {Point(element.coords[0])}")
                        print(f"End point: {Point(element.coords[-1])}")

                    # Define starting point for polygon
                    if start_point == None:
                        start_point = element.coords[0]

                    elements_array.append(element)
                    coords_array.extend(element.coords)

                    # Perform different checks to see if polygon is closed
                    if self.is_polygon_closed(elements_array) == True: # for multiple LineStrings
                        poly = self.construct_polygon(elements_array)

                        if poly != 1:
                            self.polygons.append(poly)

                    elif Point(element.coords[-1]).distance(Point(start_point)) < 1e-6: # for single LineString
                        self.polygons.append(Polygon(coords_array))

                    elif len(element.coords) == 4: # for LWPOLYLINE
                        if element.coords.xy[0][0] == element.coords.xy[0][-1]:
                            self.polygons.append(Polygon(coords_array))

                    else:
                        continue

                    start_point = None
                    elements_array = []
                    coords_array = []
                
                case Polygon():
                    self.polygons.append(element)

                case _:
                    pass

    def create_divisions(self):
        """
            Divide polygons by adding division lines into
            the `divisions` variable.

            Steps:
            1) add regular grid lines every `grid_size`,
            2) add grid lines where the vertical difference between consecutive
            vertices is large enough (avoids over-density on curves).
        """

        for polygon in self.polygons:
            min_x, min_y, max_x, max_y = polygon.bounds

            # 1) Regular horizontal grid lines
            y_grid = np.arange(min_y, max_y + self.grid_size, self.grid_size)

            # 2) Extract y-values from polygon where there's significant vertical change
            coords = list(polygon.exterior.coords)
            y_breaks = []
            for i in range(1, len(coords)):
                y_prev = coords[i - 1][1]
                y_curr = coords[i][1]

                if abs(y_curr - y_prev) >= self.min_spacing:
                    y_breaks.append(y_curr)

            # 3) Combine all y-values and deduplicate
            y_combined = np.unique(np.concatenate((y_grid, y_breaks)))
            y_combined.sort()

            # 4) Generate and clip horizontal lines
            clipped_lines = []
            for y in y_combined:
                line = LineString([(min_x, y), (max_x, y)])
                intersection = polygon.intersection(line)
                if not intersection.is_empty:
                    if intersection.geom_type == "LineString":
                        clipped_lines.append(intersection)
                    elif intersection.geom_type == "MultiLineString":
                        clipped_lines.extend(intersection.geoms)

            # Store result
            self.divisions.append(clipped_lines)

    def is_polygon_closed(self, segments, tol=1e-6):
        """
            INTERNAL FUNCTION!

            Check if given LineStrings form one closed polygon.
            
            Approach:
            1. Snap all endpoints to a grid (tol) so floating imprecision doesn't split points.
            2. Build an undirected graph where each endpoint is a node, each segment an edge.
            3. Check every node has degree exactly 2.
            4. Check the graph is a single connected component.
        """

        # 1) helper to quantize points
        def key(pt):
            return (round(pt[0]/tol)*tol, round(pt[1]/tol)*tol)
        
        # 2) build adjacency
        adj = {}
        for seg in segments:
            coords = list(seg.coords)
            a, b = key(coords[0]), key(coords[-1])
            adj.setdefault(a, set()).add(b)
            adj.setdefault(b, set()).add(a)
        
        # 3) every node must have exactly two neighbors
        for node, nbrs in adj.items():
            if len(nbrs) != 2:
                return False
        
        # 4) connectivity check (simple DFS)
        start = next(iter(adj))
        visited = set()
        stack = [start]
        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            stack.extend(adj[u] - visited)
        
        return len(visited) == len(adj)

    def construct_polygon(self, segments, tol=1e-5):
        """
            INTERNAL FUNCTION!

            Construct a single closed polygon from possibly unordered, imprecise segments.

            This version first rounds every vertex of every segment to the nearest grid
            of size tol, so endpoints that lie within tol snap exactly together.
        """

        # 0) Quantize each segment’s coords to the tol‐grid
        quantized = []
        for seg in segments:
            new_coords = [
                (round(x / tol) * tol, round(y / tol) * tol)
                for x, y in seg.coords
            ]
            quantized.append(LineString(new_coords))

        # 0.1) Print endpoints for debugging
        if self.debug == True:
            print("Segment endpoints:")
            for i, seg in enumerate(segments):
                print(f"  {i}: {seg.coords[0]} -> {seg.coords[-1]}")

        # 1) Combine into MultiLineString
        multiline = MultiLineString(quantized)

        # 2) Snap to itself to close any remaining tiny gaps
        multiline = snap(multiline, multiline, tol)

        # 3) Merge lines
        merged = linemerge(multiline)

        # 4) Polygonize
        polygons = list(polygonize(merged))

        if len(polygons) != 1:
            print(colorama.Fore.LIGHTRED_EX + f"Polygonize failed: {len(polygons)} polygons found." + colorama.Fore.RESET)

            # visualize what we got
            if isinstance(merged, LineString):
                merged = [merged]

            self.plot_lines(merged)
            return 1

        return polygons[0]
    
    def calculate_internal_angle(self, p1, p2, p3):
        """
            INTERNAL FUNCTION!

            Calculate the internal angle at p2 formed by p1-p2-p3 in degrees.
        """

        dx1 = p1[0] - p2[0]
        dy1 = p1[1] - p2[1]
        dx2 = p3[0] - p2[0]
        dy2 = p3[1] - p2[1]

        angle1 = math.atan2(dy1, dx1)
        angle2 = math.atan2(dy2, dx2)
        angle_diff = abs(angle1 - angle2)

        return math.degrees(min(angle_diff, 2 * np.pi - angle_diff))

    def is_diagonal(self, p1, p2, slope_threshold=0.05):
        """
            INTERNAL FUNCTION!

            Return True if segment is not approximately horizontal or vertical.
        """

        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        if dx == 0 or dy == 0:
            return False  # horizontal or vertical

        slope = abs(dy / dx)
        return slope > slope_threshold and slope < (1 / slope_threshold)

    def filter_dense_y_coords(self, y_coords, min_gap=2.0):
        """
            INTERNAL FUNCTION!

            Filter out y-values that are too close to each other.
        """

        y_coords = sorted(set(y_coords))
        filtered = []
        last_y = None

        for y in y_coords:
            if last_y is None or abs(y - last_y) >= min_gap:
                filtered.append(y)
                last_y = y

        return filtered

    def plot_lines(self, lines):
        """
            DEBUG FUNCTION!

            Plot lines.
        """

        fig, ax = plt.subplots(figsize=(8, 8))
        for line in lines:
            if isinstance(line, LineString):
                x, y = line.xy  # Get the coordinates of the line
                ax.plot(x, y, color='blue', lw=2)  # Plot the line in blue with a line width of 2

        # Show the plot with the lines
        plt.title("Detected Lines")
        plt.gca().set_aspect('equal', adjustable='box')  # Set equal aspect ratio
        plt.show()


    def plot_shape(self):
        """
            DEBUG FUNCTION!

            Plot polygons.
        """

        plt.figure(figsize=(8, 8))
        for polygon in self.polygons:
            if isinstance(polygon, Polygon):
                x, y = polygon.exterior.xy  # Extract x and y coordinates
                plt.plot(x, y, color='blue', linewidth=2)
                plt.fill(x, y, color='lightblue', alpha=0.5)  # Optional: fill the polygon
                plt.title('Polygon Plot')
                plt.xlabel('X')
                plt.ylabel('Y')
                plt.grid(True)

            elif isinstance(polygon, MultiPolygon):
                for geom in polygon.geoms:
                    xs, ys = geom.exterior.xy
                    plt.fill(xs, ys, alpha=0.5, fc='r', ec='none')

        plt.show()

    def plot_grid(self) -> None:
        """
            Plot divided polygons on the screen.
        """

        fig, ax = plt.subplots()
        for polygon, division in zip(self.polygons, self.divisions):
            if isinstance(polygon, Polygon):
                # Plot the polygon
                x, y = polygon.exterior.xy
                ax.plot(x, y, color='black')

            elif isinstance(polygon, MultiPolygon):
                for geom in polygon.geoms:
                    xs, ys = geom.exterior.xy    
                    ax.fill(xs, ys, alpha=0.5, fc='r', ec='none')

            # Plot the divisions
            for line in division:
                if isinstance(line, LineString):
                    x, y = line.xy
                    ax.plot(x, y, color='blue')
                elif isinstance(line, Polygon):
                    x, y = line.exterior.xy  # Fix: Directly get exterior coordinates
                    ax.plot(x, y, color='blue')
                elif isinstance(line, MultiPolygon):
                    for geom in line.geoms:
                        x, y = geom.exterior.xy
                        ax.plot(x, y, color='blue')

        plt.show()

    def get_shapes(self):
        """
            Return polygons and their divisions.
        """

        return (self.polygons, self.divisions)
