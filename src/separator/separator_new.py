# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Separator entry file

import colorama
import matplotlib.pyplot as plt
from shapely.geometry import LineString, MultiPolygon, Point, Polygon

class Separator_NEW:
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

        # Variable holding polygons/shapes
        self.polygons = []

        # Variable holding divisions for each polygon
        self.divisions = []

        # Variable holding grid size
        self.grid_size = 25

        self.create_polygons()
        self.create_divisions()

    # TODO! Complete this.
    def create_polygons(self):
        """
            Create a polygon from Shapely elements.
        """

        start_point = None
        temp_array = []

        print(self.elements)
        for element in self.elements:
            match element:
                case LineString():
                    if start_point != None:
                        print(colorama.Fore.LIGHTRED_EX + f"REFERENCE: {Point(start_point)}" + colorama.Fore.RESET)
                    print(f"Start point: {Point(element.coords[0])}")
                    print(f"End point: {Point(element.coords[-1])}")

                    if start_point == None:
                        start_point = element.coords[0]
                        temp_array.extend(element.coords)
                    
                    # TODO! This doesn't ensure polygon is closed.
                    elif Point(element.coords[-1]).distance(Point(start_point)) < 1e-6:
                        temp_array.extend(element.coords)
                        self.polygons.append(Polygon(temp_array))
                        start_point = None

                    else:
                        temp_array.extend(element.coords)

                
                case Polygon():
                    self.polygons.append(element)

                case _:
                    pass

        print(len(self.polygons))

    # TODO! Reimplement this.
    def create_divisions(self):
        pass

    def plot_lines(self):
        """
            DEBUG FUNCTION!

            Plot lines.
        """

        fig, ax = plt.subplots(figsize=(8, 8))
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
        return (self.polygons, self.divisions)
