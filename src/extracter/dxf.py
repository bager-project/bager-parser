# AUTHOR Andrej Bartulin, EndermanPC
# PROJECT: B.A.G.E.R. parser
# LICENSE: 
# DESCRIPTION: .dxf extracter entry file

import ezdxf
import os
from shapely.geometry import LineString

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

        if not os.path.exists(path):
            print(f"File in path {path} does not exist!")
            print("Exiting...")

            exit(0)

        self.doc = ezdxf.readfile(path)
        self.modelspace = self.doc.modelspace()

        self.extract_entities()

    # Run parser
    def get_elements(self):
        return self.elements

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

    # Print found entities
    def print_entities(self) -> None:
        # Extract different types of elements
        for element_type, entities in self.elements.items():
            print(f"{element_type}: {len(entities)} entities found")
            for entity in entities:
                print(entity)
