# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Entry file

import colorama
import os
import sys
import toml

from extractor.dxf import *
from extractor.image import *
from lexer.lexer import *
from positioner.positioner import *
from separator.separator import *

if __name__ == "__main__":
    config_path: str = ""

    if len(sys.argv) < 2:
        config_path = input("Enter config path: ")
    
    else:
        config_path = sys.argv[1]

    if not os.path.exists(config_path):
        print(f"File in path {config_path} not found!")
        print("Exiting...")
        
        exit(0)

    parsed_toml = toml.load(config_path)
    print(colorama.Fore.LIGHTRED_EX + "B.A.G.E.R. parser" + colorama.Fore.RESET)

    extractor = None

    if (parsed_toml['extractor']['type'] == "dxf"):
        extractor = DXF(parsed_toml['paths']['dxf_path'])

    elif (parsed_toml["extractor"]['type'] == "image"):
        extractor = Image(parsed_toml['paths']['image_path'])

    if extractor != None:
        extractor.extract_entities()
        elements = extractor.get_elements()

        separator = Separator(elements)
        separator.execute()
        polygons, grids = separator.get_shapes()

        positioner = Positioner(parsed_toml['paths']['position_path'], polygons, grids)
        positioner.execute()
        transformed_polygons, transformed_grids = positioner.get_elements()

        lexer = Lexer(transformed_polygons, transformed_grids)
        lexer.execute()
        lexer.plot_grid()
