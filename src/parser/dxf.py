# AUTHOR Andrej Bartulin, EndermanPC
# PROJECT: B.A.G.E.R. parser
# LICENSE: 
# DESCRIPTION: .dxf parser entry file

import ezdxf
import matplotlib.pyplot as plt
import numpy as np
import os
from shapely.geometry import LineString, Polygon

# DXF parser
class DXF:

    # Initialize all variables
    def __init__(self, path) -> None:
        self.path = path
    
        # Dictionary to store all elements
        self.elements = {
            'LINES': [],
            'LWPOLYLINE': [],
            'DIMENSIONS': [],
            "UNIMPLEMENTED": [],
        }

        # Variable holding grid / divisions 
        self.grid = None

        # Variable holding polygon
        self.polygon = None

        if not os.path.exists(path):
            print(f"File in path {path} does not exist!")
            print("Exiting...")

            exit(0)

        self.doc = ezdxf.readfile(path)
        self.modelspace = self.doc.modelspace()

    # Run parser
    def execute(self) -> None:
        self.extract_entities()

        grid_size = 10

        polygon_result:int = self.create_polygon()
        if polygon_result != 0:
            return

        self.create_divisions(grid_size)
        self.plot_shape_and_grid()

    # Extract .dxf entities
    def extract_entities(self) -> None:
        # Extract different types of elements
        for entity in self.modelspace:
            match entity.dxftype():
                case 'LINE':
                    start_point = (entity.dxf.start.x, entity.dxf.start.y)
                    end_point = (entity.dxf.end.x, entity.dxf.end.y)

                    self.elements['LINES'].append(LineString([start_point, end_point]))

                case 'LWPOLYLINE':
                    self.elements['LWPOLYLINE'].append(entity)

                case 'DIMENSION':
                    self.elements['DIMENSIONS'].append(entity)

                case _:
                    self.elements['UNIMPLEMENTED'].append(entity)

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

    # Print found entities
    def print_entities(self) -> None:
        # Extract different types of elements
        for element_type, entities in self.elements.items():
            print(f"{element_type}: {len(entities)} entities found")
            for entity in entities:
                print(entity)
