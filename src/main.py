# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: 
# DESCRIPTION: Entry file

import colorama
import sys

from parser.dxf import *
from config.position import *

if __name__ == "__main__":
    dxf_path: str = ""
    position_path: str = ""

    if len(sys.argv) < 3:
        dxf_path = input("Enter .dxf file path: ")
        position_path = input("Enter POSITION.toml file path: ")
    
    else:
        dxf_path = sys.argv[1]
        position_path = sys.argv[2]

    print(colorama.Fore.LIGHTRED_EX + "B.A.G.E.R. parser" + colorama.Fore.RESET)

    position = Position(position_path)

    dxf = DXF(dxf_path)
    dxf.execute()
