# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: 
# DESCRIPTION: Entry file

import sys

from dxf.dxf import *
from position.position import *

if __name__ == "__main__":
    dxf_path: str = ""
    position_path: str = ""

    if len(sys.argv) < 3:
        dxf_path = input("Enter .dxf file path: ")
        position_path = input("Enter POSITION.toml file path: ")
    
    else:
        dxf_path = sys.argv[1]
        position_path = sys.argv[2]

    print("B.A.G.E.R. parser")

    position = Position(position_path)
    dxf = DXF(dxf_path)
