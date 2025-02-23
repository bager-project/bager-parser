# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Separator entry file

import cv2
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString, MultiPolygon, Point, Polygon

class Separator:
    """
        Create a polygon from extracted entities
        and divide them into smaller divisions/cells.

        Attributes:
            elements(list): extracted entities converted into a Shapely form
    """

    def __init__(self, elements):
        """
            Initialize all the variables.
        """

        self.elements = elements

        # Variable holding divisions of each polygon
        self.divisions = []

        # Variable holding polygons/shapes
        self.polygons = []

        # Variable holding grid size
        self.grid_size = 10

        polygon_result:int = self.create_polygon()
        if polygon_result != 0:
            return
        
        self.create_divisions()

    def create_polygon(self) -> int:
        """
            Create a polygon from extracted
            Shapely elements.
        """
        all_coords = []
        start_point = None

        if len(self.elements) == 0:
            print("No element found to create polygons!")
            return 1
        
        for arc in self.elements['ARC']:
            arc_coords = list(arc.coords)
            all_coords.extend(arc_coords)

            # Check if the shape is closed
            if start_point is None:
                start_point = arc_coords[0]

            elif Point(arc_coords[-1]).distance(Point(start_point)) < 1e-6:
                self.polygons.append(Polygon(all_coords))
                all_coords = []
                start_point = None

        for circle in self.elements['CIRCLE']:
            self.polygons.append(circle)

        for ellipse in self.elements['ELLIPSE']:
            self.polygons.append(ellipse)

        for line in self.elements['LINE']:
            all_coords.extend(line.coords)

            # Check if the shape is closed
            if start_point is None:
                start_point = line.coords[0]

            elif Point(line.coords[-1]).distance(Point(start_point)) < 1e-6:  # Small threshold for floating-point precision
                self.polygons.append(Polygon(all_coords))
                all_coords = []
                start_point = None

        for polyline in self.elements['LWPOLYLINE']:
            all_coords.extend(polyline.coords)

            # Check if the shape is closed
            if (polyline.coords.xy[0][0] == polyline.coords.xy[0][-1]):
                self.polygons.append(Polygon(all_coords))
                all_coords = []

        for spline in self.elements['SPLINE']:
            all_coords.extend(spline.coords)

            # Check if the shape is closed
            if len(all_coords) > 2 and all_coords[0] == all_coords[-1]:
                self.polygons.append(Polygon(all_coords))
                all_coords = []

        if len(self.elements['POINTS']):
            # Create polygons from points using convex hulls
            points = np.array(self.elements['POINTS'])
            hull = cv2.convexHull(points)

            self.polygons.append(Polygon(hull.squeeze()))

        # If there are leftover lines, create a polygon from them
        if all_coords:
            self.polygons.append(Polygon(all_coords))

        return 0

    def create_divisions(self):
        """
            Divide each polygon by adding division lines into
            the `grids` variable.

            First, add lines at regular interval defined in
            `grid_size` variable and then, in case of straight
            line, add additional lines from each breakpoint/edge.
        """

        # Tolerance for curved lines
        tolerance = self.grid_size * 0.01
        
        for polygon in self.polygons:
            min_x, min_y, max_x, max_y = polygon.bounds
            
            # 1) Regular grid lines
            y_grid = np.arange(min_y, max_y + self.grid_size, self.grid_size)
            
            # 2) Polygon breakpoints (y-coords of vertices)
            # Only include a vertex if its y is nearly the same as its neighbors,
            # which indicates a straight (horizontal) segment.
            coords = list(polygon.exterior.coords)

            # Exclude the duplicate last point.
            n = len(coords) - 1  
            y_breakpoints = []

            for i in range(n):
                y_current = coords[i][1]

                # Wrap-around: use the previous vertex (or the last one if at index 0)
                y_prev = coords[i-1][1] if i > 0 else coords[n-1][1]
                y_next = coords[(i+1) % n][1]

                # Only include if the vertical differences are below the tolerance.
                if abs(y_current - y_prev) < tolerance and abs(y_current - y_next) < tolerance:
                    y_breakpoints.append(y_current)
            
            # 3) Combine & sort unique y-values
            y_combined = np.unique(np.concatenate((y_grid, y_breakpoints)))
            y_combined.sort()
            
            # 4) Create and clip each horizontal line to the polygon
            clipped_lines = []
            for y in y_combined:
                line = LineString([(min_x, y), (max_x, y)])
                intersection = polygon.intersection(line)
                if not intersection.is_empty:
                    if intersection.geom_type == "LineString":
                        clipped_lines.append(intersection)
                    elif intersection.geom_type == "MultiLineString":
                        clipped_lines.extend(intersection.geoms)
            
            # Store the final lines for this polygon
            self.divisions.append(clipped_lines)

    def plot_lines(self):
        """
            DEBUG FUNCTION!

            Plot lines.
        """
        fig, ax = plt.subplots(figsize=(8, 8))

        # Loop over each detected line in the list
        for line in self.elements['LINE']:
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
        for polygon in self.polygons:
            x, y = polygon.exterior.xy  # Extract x and y coordinates
            plt.figure(figsize=(8, 8))
            plt.plot(x, y, color='blue', linewidth=2)
            plt.fill(x, y, color='lightblue', alpha=0.5)  # Optional: fill the polygon
            plt.title('Polygon Plot')
            plt.xlabel('X')
            plt.ylabel('Y')
            plt.grid(True)

        plt.show()
    
    def plot_grid(self) -> None:
        """
            Plot divided polygons on the screen.
        """

        fig, ax = plt.subplots()

        for polygon, division in zip(self.polygons, self.divisions):
            # Plot the polygon
            x, y = polygon.exterior.xy
            ax.plot(x, y, color='black')

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
