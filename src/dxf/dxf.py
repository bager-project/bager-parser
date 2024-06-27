# AUTHOR Andrej Bartulin, EndermanPC
# PROJECT: B.A.G.E.R. parser
# LICENSE: 
# DESCRIPTION: .dxf parser entry file

import ezdxf
import numpy as np

class DXF:
    def __init__(self, path) -> None:
        self.path = path;
        self.points = []
    
        # Dictionary to store all elements
        self.elements = {
            'LINES': [],
            'DIMENSIONS': [],
            "UNIMPLEMENTED": [],
        }

        self.doc = ezdxf.readfile(path)

        # Get the modelspace
        self.modelspace = self.doc.modelspace()

        self.extract_entities()

    def extract_entities(self) -> None:
        # Extract different types of elements
        for entity in self.modelspace:
            match entity.dxftype():
                case 'LINE':
                    self.elements['LINES'].append(entity)

                    self.points.append((entity.dxf.start.x, entity.dxf.end.x))

                case 'DIMENSION':
                    self.elements['DIMENSIONS'].append(entity)

                case _:
                    self.elements['UNIMPLEMENTED'].append(entity)

        self.create_grid()

    def create_grid(self) -> None:
        x_coords, y_coords = zip(*self.points)

        min_x = min(x_coords)
        max_x = max(x_coords)
        min_y = min(y_coords)
        max_y = max(y_coords)

        x_range = np.arange(min_x, max_x, (max_x - min_x))
        y_range = np.arange(min_y, max_y, 10)
        grid = [(x, y) for x in x_range for y in y_range]
        
        for i, center in enumerate(grid):
            print(f"Moving to square: {i+1} at center: {center}")

    def print_entities(self) -> None:
        # Extract different types of elements
        for element_type, entities in self.elements.items():
            print(f"{element_type}: {len(entities)} entities found")
            for entity in entities:
                print(entity)
