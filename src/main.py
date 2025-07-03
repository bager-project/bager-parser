# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Entry file

import colorama
import os
import sys
import toml

from embedder.embedder import *
from extractor.dxf import *
from extractor.image import *
from positioner.positioner import *
from separator.separator import *

def parse(parsed_toml, section_name):
    """
        Parse (run extractor, separator, positioner and embedder) each
        TOML section in `config.toml`.
    """

    extractor = None

    match parsed_toml[section_name]['parser_type']:
        case "dxf":
            extractor = DXF(parsed_toml[section_name]['path'])

        case "image":
            extractor = Image(parsed_toml[section_name]['path'])

        case _:
            pass

    if extractor != None:
        extractor.extract_entities()
        elements = extractor.get_elements()

        separator = Separator(elements)
        separator.execute()
        polygons, grids = separator.get_shapes()

        positioner = Positioner(parsed_toml[section_name]['position_path'], 
                                parsed_toml[section_name]['depth'], polygons, grids)
        positioner.execute()
        transformed_polygons, transformed_grids = positioner.get_elements()

        embedder = Embedder(transformed_polygons, transformed_grids, parsed_toml, section_name)
        embedder.execute()
        embedder.plot_polygons()

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

    # Loop through each TOML section and parse it
    for key, value in parsed_toml.items():
        if isinstance(value, dict):
            parse(parsed_toml, key)
