# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: 
# DESCRIPTION: .dxf parser entry file

import ezdxf

class DXF:
    def __init__(self, path) -> None:
        self.path = path;
    
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
        self.print_entities()

    def extract_entities(self) -> None:
        # Extract different types of elements
        for entity in self.modelspace:
            match entity.dxftype():
                case 'LINE':
                    self.elements['LINES'].append(entity)
                    print(entity.dxf.start)

                case 'DIMENSION':
                    self.elements['DIMENSIONS'].append(entity)

                case _:
                    self.elements['UNIMPLEMENTED'].append(entity)

    def print_entities(self) -> None:
        # Extract different types of elements
        for element_type, entities in self.elements.items():
            print(f"{element_type}: {len(entities)} entities found")
            for entity in entities:
                print(entity)
