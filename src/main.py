# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Entry file

import colorama
import os
import sys
import toml

from config.position import *
from extractor.dxf import *
from extractor.dxf_new import *
from extractor.image import *
from lexer.lexer import *
from positioner.positioner import *
from separator.separator import *
from separator.separator_new import *

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

    position = Position(parsed_toml['paths']['position_path'])
    extractor = None

    if (parsed_toml['extractor']['type'] == "dxf"):
        extractor = DXF(parsed_toml['paths']['dxf_path'])
        extractor_new = DXF_NEW(parsed_toml['paths']['dxf_path'])

    elif (parsed_toml["extractor"]['type'] == "image"):
        extractor = Image(parsed_toml['paths']['image_path'])
        extractor.execute()

    if extractor != None:
        extractor_new.extract_entities()
        elements_new = extractor_new.get_elements()

        separator_new = Separator_NEW(elements_new)
        polygons, grids = separator_new.get_shapes()

        separator_new.plot_shape()

    exit(0)

    if extractor != None:
        elements = extractor.get_elements()
        separator = Separator(elements)

        polygons, grids = separator.get_shapes()

        # positioner = Positioner(polygons, grids)
        lexer = Lexer(polygons, grids)

        # positioner.execute()
        lexer.execute()
        
        separator.plot_grid()
