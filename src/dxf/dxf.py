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

        for line in self.lines:
            all_coords.extend(line.coords)
        bounds = Polygon(all_coords).bounds
        
        grid = self.create_divisions(bounds, grid_size)
        self.plot_shape_and_grid(self.lines, grid)

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

    def create_divisions(self, bounds, division_number) -> None:
        min_x, min_y, max_x, max_y = bounds
        y_points = np.arange(min_y, max_y, division_number)
        
        horizontal_lines = []
        for y in y_points:
            horizontal_line = LineString([(min_x, y), (max_x, y)])
            horizontal_lines.append(horizontal_line)
        
        return horizontal_lines
    
    def plot_shape_and_grid(self, lines, divisions):
        fig, ax = plt.subplots()
        for line in lines:
            x, y = line.xy
            ax.plot(x, y, color='black')

        for division in divisions:
            x, y = division.xy
            ax.plot(x, y, color='blue')

        plt.show()

    def print_entities(self) -> None:
        # Extract different types of elements
        for element_type, entities in self.elements.items():
            print(f"{element_type}: {len(entities)} entities found")
            for entity in entities:
                print(entity)
