# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Lexer entry file

import matplotlib.pyplot as plt
from shapely.geometry import LineString, MultiPolygon, Polygon

class Lexer:
    """
        Tokenize every polygon division.

        Attributes:
            polygons(list): list of polygons
            divisions(list): list of lines (divisions) FOR EACH polygon
    """

    def __init__(self, polygons, divisions):
        """
            Initialize all the variables.
        """

        self.polygons = polygons
        self.divisions = divisions

    def execute(self):
        """
            Tokenize.
        """
        
        for polygon, division in zip(self.polygons, self.divisions):
            print("--- SHAPE ----: ")
            print(polygon)

            print("--- DIVISIONS ---: ")
            for line in division:
                print(line)
            
            print("----------------------------------------")

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
