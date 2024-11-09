# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: 
# DESCRIPTION: separator entry file

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString, Polygon

class Separator:

    # Initialize all variables
    def __init__(self, elements):
        self.elements = elements

        # Variable holding grid / divisions 
        self.grid = None

        # Variable holding polygon
        self.polygon = None

        # Variable holding grid size
        grid_size = 10

        polygon_result:int = self.create_polygon()
        if polygon_result != 0:
            return

        self.create_divisions(grid_size)
        self.plot_shape_and_grid()

    # Create polygon from extracted entities
    def create_polygon(self) -> int:
        all_coords = []

        if len(self.elements['LINES']):
            for line in self.elements['LINES']:
                all_coords.extend(line.coords)

        elif len(self.elements['LWPOLYLINE']):
            for polyline in self.elements['LWPOLYLINE']:
                all_coords.extend(polyline.get_points('xy'))

        else:
            print("No element found to create polygon!")
            return 1

        self.polygon = Polygon(all_coords)
        return 0

    # Divide polygon into smaller pieces
    def create_divisions(self, division_number):
        min_x, min_y, max_x, max_y = self.polygon.bounds
        y_points = np.arange(min_y, max_y, division_number)
        
        horizontal_lines = []
        for y in y_points:
            horizontal_line = LineString([(min_x, y), (max_x, y)])
            horizontal_lines.append(horizontal_line)
        
        clipped_lines = []
        for line in horizontal_lines:
            clipped_line = self.polygon.intersection(line)
            if not clipped_line.is_empty:
                clipped_lines.append(clipped_line)
        
        self.grid = clipped_lines
    
    # Plot divided polygon on screen
    def plot_shape_and_grid(self) -> None:
        fig, ax = plt.subplots()
    
        # Plot the polygon
        x, y = self.polygon.exterior.xy
        ax.plot(x, y, color='black')
        
        # Plot the divisions
        for division in self.grid:
            if isinstance(division, LineString):
                x, y = division.xy
                ax.plot(x, y, color='blue')
            elif isinstance(division, Polygon):
                for geom in division.geoms:
                    x, y = geom.exterior.xy
                    ax.plot(x, y, color='blue')

        plt.show()
