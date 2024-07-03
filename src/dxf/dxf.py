# AUTHOR Andrej Bartulin, EndermanPC
# PROJECT: B.A.G.E.R. parser
# LICENSE: 
# DESCRIPTION: .dxf parser entry file

import ezdxf
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString, Polygon
from shapely.ops import split

class DXF:
    def __init__(self, path) -> None:
        self.path = path;
        self.lines = []
    
        # Dictionary to store all elements
        self.elements = {
            'LINES': [],
            'DIMENSIONS': [],
            "UNIMPLEMENTED": [],
        }

        self.doc = ezdxf.readfile(path)
        self.modelspace = self.doc.modelspace()

    def execute(self) -> None:
        self.extract_entities()

        grid_size = 10
        all_coords = []

        # Create a polygon from the lines
        polygon = self.create_polygon()
        
        # Create horizontal divisions
        divisions = self.create_divisions(polygon, grid_size)
        
        # Plot the shape and the divisions
        self.plot_shape_and_grid(polygon, divisions)

    def extract_entities(self) -> None:
        # Extract different types of elements
        for entity in self.modelspace:
            match entity.dxftype():
                case 'LINE':
                    self.elements['LINES'].append(entity)

                    start_point = (entity.dxf.start.x, entity.dxf.start.y)
                    end_point = (entity.dxf.end.x, entity.dxf.end.y)
                    self.lines.append(LineString([start_point, end_point]))

                case 'DIMENSION':
                    self.elements['DIMENSIONS'].append(entity)

                case _:
                    self.elements['UNIMPLEMENTED'].append(entity)

    def create_polygon(self) -> Polygon:
        all_coords = []
        for line in self.lines:
            all_coords.extend(line.coords)

        return Polygon(all_coords)

    def create_divisions(self, polygon: Polygon, division_number):
        min_x, min_y, max_x, max_y = polygon.bounds
        y_points = np.arange(min_y, max_y, division_number)
        
        horizontal_lines = []
        for y in y_points:
            horizontal_line = LineString([(min_x, y), (max_x, y)])
            horizontal_lines.append(horizontal_line)
        
        clipped_lines = []
        for line in horizontal_lines:
            clipped_line = polygon.intersection(line)
            if not clipped_line.is_empty:
                clipped_lines.append(clipped_line)
        
        return clipped_lines
    
    def plot_shape_and_grid(self, polygon, divisions):
        fig, ax = plt.subplots()
    
        # Plot the polygon
        x, y = polygon.exterior.xy
        ax.plot(x, y, color='black')
        
        # Plot the divisions
        for division in divisions:
            if isinstance(division, LineString):
                x, y = division.xy
                ax.plot(x, y, color='blue')
            elif isinstance(division, Polygon):
                for geom in division.geoms:
                    x, y = geom.exterior.xy
                    ax.plot(x, y, color='blue')

        plt.show()

    def print_entities(self) -> None:
        # Extract different types of elements
        for element_type, entities in self.elements.items():
            print(f"{element_type}: {len(entities)} entities found")
            for entity in entities:
                print(entity)
