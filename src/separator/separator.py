# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Separator

from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString, MultiPolygon, Polygon

class Separator:
    """
        Create a polygon from Shapely elements
        and divide them into smaller divisions/cells.

        Attributes:
            elements(list): Shapely elements
            debug: is debug mode on
            grid_size: size of the grid
            min_spacing: minimum spacing between two lines in a grid
    """

    def __init__(self, elements, debug, grid_size, min_spacing):
        """
            Initialize all the variables.
        """

        self.elements = elements

        # Are we in debug mode
        self.debug = debug

        # Variable holding polygons/shapes
        self.polygons = []

        # Variable holding divisions for each polygon
        self.divisions = []

        # Variable holding grid size
        self.grid_size = grid_size

        # Variable holding minimal spacing in curved segments
        self.min_spacing = min_spacing

    def execute(self):
        self.create_polygons()

        if len(self.polygons) != 0:
            self.create_divisions()

    ###########################################################################
    #####                                                                 #####
    ###########################################################################

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

    def create_polygons(self):
        """
            Create a polygon from Shapely elements.
        """

        elements_linestring = []

        if self.debug == True:
            print(f"[SEPARATOR-DEBUG] Extracted Shapely elements: \n{self.elements}.\n")

        for element in self.elements:
            match element:
                case LineString():
                    elements_linestring.append(element)
                
                case Polygon():
                    self.polygons.append(element)

                case _:
                    pass

        segments = self.linestrings_to_segments(elements_linestring)
        self.polygons.extend(self.find_polygons(segments))

    def get_shapes(self):
        """
            Return polygons and their divisions.
        """

        return (self.polygons, self.divisions)

    ###########################################################################
    #####                                                                 #####
    ###########################################################################

    def build_adjacency(self, lines):
        """
            INTERNAL FUNCTION!

            Build an adjacency list mapping each endpoint to connected lines
            and their opposite endpoints.
        """

        adj = defaultdict(list)
        for idx, line in enumerate(lines):
            p1r = self.round_point(tuple(line.coords[0]))
            p2r = self.round_point(tuple(line.coords[-1]))

            adj[p1r].append((idx, p2r))
            adj[p2r].append((idx, p1r))

        return adj

    def canonical_ring_key(self, coords):
        """
            INTERNAL FUNCTION!

            Get canonical form of ring to avoid duplicates.
        """

        coords = coords[:-1] if coords[0] == coords[-1] else coords
        n = len(coords)

        rotations = [tuple(coords[i:] + coords[:i]) for i in range(n)]
        rotations_rev = [tuple(reversed(r)) for r in rotations]

        return min(rotations + rotations_rev)

    def find_polygons(self, lines):
        """
            INTERNAL FUNCTION!

            Find all closed, non intersecting polygons in array of
            `LineString` objects.
        """

        # Ensure lines are LineStrings
        adj = self.build_adjacency(lines)
        polygons = []
        seen_polygons = set()

        def dfs(path, used_edges):
            """
                Perform DFS algorithm to find neighboring lines.
            """

            current = self.round_point(path[-1])
            for idx, neighbor in adj[current]:
                if idx in used_edges:
                    continue

                used_edges.add(idx)
                path.append(neighbor)

                if neighbor == path[0] and len(path) >= 4:
                    ring = path[:]
                    polygon = Polygon(ring)

                    if polygon.is_valid and polygon.is_simple:
                        key = self.canonical_ring_key(ring)
                        if key not in seen_polygons:
                            seen_polygons.add(key)
                            polygons.append(polygon)

                elif neighbor not in path[:-1]:
                    dfs(path, used_edges)

                path.pop()
                used_edges.remove(idx)

        for idx, line in enumerate(lines):
            p1r = self.round_point(tuple(line.coords[0]))
            p2r = self.round_point(tuple(line.coords[-1]))
            dfs([p1r, p2r], {idx})

        return polygons
    
    def linestrings_to_segments(self, lines):
        """
            INTERNAL FUNCTION!

            Convert `LineString` objects into segments.
        """
        segments = []
        for line in lines:
            coords = list(line.coords)
            for i in range(len(coords) - 1):
                segments.append(LineString([coords[i], coords[i + 1]]))

        return segments
    
    def round_point(self, pt):
        """
            INTERNAL FUNCTION!

            Round a point.
        """

        precision = 6
        return (round(pt[0], precision), round(pt[1], precision))

    ###########################################################################
    #####                                                                 #####
    ###########################################################################

    def plot_grid(self) -> None:
        """
            DEBUG FUNCTION!

            Plot polygons and their divisions on the screen.
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
