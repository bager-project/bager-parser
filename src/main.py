# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: 
# DESCRIPTION: Entry file

import colorama
import os
import sys
import toml

from config.position import *
from parser.dxf import *
from tree.ast import *

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

    position = Position(parsed_toml['position_path'])

    dxf = DXF(parsed_toml["dxf_path"])
    dxf.execute()
