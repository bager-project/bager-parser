# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Lexer entry file

import math
import matplotlib.pyplot as plt
from shapely.geometry import LineString, MultiPolygon, Polygon, box
from shapely.ops import split

class Embedder:
    """
        Embed divided polygons into a file which will be
        passed to the Raspberry Pi Pico.

        Attributes:
            polygons(list): list of polygons
            divisions(list): list of lines (divisions) FOR EACH polygon
    """

    def __init__(self, polygons, divisions, parsed_toml, section_name):
        """
            Initialize all the variables.
        """

        self.polygons = polygons
        self.divisions = divisions

        self.parsed_toml = parsed_toml
        self.section_name: str = section_name

        self.text = ""

        self.debug = False
        self.divided_polygons = []

    def execute(self):
        """
            Embed.
        """

        if self.debug == True:
            for polygon, division in zip(self.polygons, self.divisions):
                print("--- SHAPE ----: ")
                print(polygon)

                print("--- DIVISIONS ---: ")
                for line in division:
                    print(line)
                
                print("----------------------------------------")
        
        self.polygonize()

        self.text += self.section_name.upper()
        self.text += "-"
        self.text += str(self.parsed_toml[self.section_name]['hole']).upper()
        self.text += "\n"

        for i in range(len(self.divided_polygons)):
            if self.debug == True:
                print(f"--- POLYGON {i} ---: ")

            self.text += f"\tPOLYGON {i}\n"

            for polygon in self.divided_polygons[i]:
                if self.debug == True:
                    print(f"\t{polygon}")

                self.text += f"\t\t{polygon}\n"

        print(self.text)

        with open("documentation.txt", "a") as file:
            file.write(self.text)

    ###########################################################################
    #####                                                                 #####
    ###########################################################################

    def polygonize(self):
        """
            Split all polygons in `self.polygons`
            into smaller polygons based on LineString divisions.
        """
        for polygon, division in zip(self.polygons, self.divisions):
            for i in range(len(division)):
                division[i] = self.extend_line(division[i], polygon.bounds)

            result = self.split_polygons(polygon, division)
            self.divided_polygons.append(result)

    ###########################################################################
    #####                                                                 #####
    ###########################################################################

    def extend_line(self, line, bounds, extension=1.0):
        """
            INTERNAL FUNCTION!

            Extend a line in both directions beyond its endpoints.
        """

        (x1, y1), (x2, y2) = list(line.coords)

        # Direction vector
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)

        # Normalize direction
        dx /= length
        dy /= length

        # Extend beyond bounds in both directions
        minx, miny, maxx, maxy = bounds
        diag = math.hypot(maxx - minx, maxy - miny)
        extend_by = diag + extension

        new_start = (x1 - dx * extend_by, y1 - dy * extend_by)
        new_end   = (x2 + dx * extend_by, y2 + dy * extend_by)

        return LineString([new_start, new_end])

    def split_polygons(self, polygon, lines):
        """
            INTERNAL FUNCTION!

            Split a polygon into smaller polygons based
            on LineString divisions.
        """

        result = [polygon]

        for line in lines:
            temp_result = []
            for poly in result:
                try:
                    # Only split if line actually intersects polygon
                    if line.intersects(poly):
                        split_parts = split(poly, line)
                        temp_result.extend([g for g in split_parts.geoms if g.geom_type == 'Polygon'])
                    else:
                        temp_result.append(poly)

                except Exception as e:
                    print(f"Error splitting polygon: {e}")
                    temp_result.append(poly)

            result = temp_result

        return result
    
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

    def plot_polygons(self):
        """
            DEBUG FUNCTION!

            Plot polygons in `self.divided_polygons`.
        """

        fig, ax = plt.subplots()
        for i in range(len(self.divided_polygons)):
            for polygon in self.divided_polygons[i]:
                if isinstance(polygon, Polygon):
                    # Plot the polygon
                    x, y = polygon.exterior.xy
                    ax.plot(x, y, color='black')

                elif isinstance(polygon, MultiPolygon):
                    for geom in polygon.geoms:
                        xs, ys = geom.exterior.xy    
                        ax.fill(xs, ys, alpha=0.5, fc='r', ec='none')

        plt.show()
