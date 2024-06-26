import ezdxf

if __name__ == "__main__":
    print("B.A.G.E.R. parser")

    doc = ezdxf.readfile("../square.dxf")

    # Get the modelspace
    modelspace = doc.modelspace()
    
    # Dictionary to store all elements
    elements = {
        'LINES': [],
        'DIMENSIONS': [],
        "UNIMPLEMENTED": [],
    }
    
    # Extract different types of elements
    for entity in modelspace:
        match entity.dxftype():
            case 'LINE':
                elements['LINES'].append(entity)

            case 'DIMENSION':
                elements['DIMENSIONS'].append(entity)

            case _:
                elements['UNIMPLEMENTED'].append(entity)


    for element_type, entities in elements.items():
        print(f"{element_type}: {len(entities)} entities found")
        for entity in entities:
            print(entity)
