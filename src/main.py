# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: 
# DESCRIPTION: Entry file

import sys

from dxf.dxf import *

if __name__ == "__main__":
    path: str = ""

    if len(sys.argv) < 2:
        path = input("Enter .dxf file path: ")
    
    else:
        path = sys.argv[1]

    print("B.A.G.E.R. parser")

    dxf = DXF(path)
