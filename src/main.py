# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Entry file

import colorama
import os
import sys
import threading
import toml

from config.position import *
from extractor.dxf import *
from extractor.image import *
from lexer.lexer import *
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

    position = Position(parsed_toml['paths']['position_path'])
    extractor = None

    if (parsed_toml['extractor']['type'] == "dxf"):
        extractor = DXF(parsed_toml['paths']['dxf_path'])

    elif (parsed_toml["extractor"]['type'] == "image"):
        extractor = Image(parsed_toml['paths']['image_path'])
        extractor.execute()

    if extractor != None:
        elements = extractor.get_elements()
        separator = Separator(elements)

        polygons, grids = separator.get_shapes()
        lexer = Lexer(polygons, grids)

        thread1 = threading.Thread(target=lexer.execute())
        thread2 = threading.Thread(target=separator.plot_grid())

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()
