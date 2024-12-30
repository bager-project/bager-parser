# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Lexer entry file

class Lexer:
    
    # Initialize all variables
    def __init__(self, polygons, grids):
        self.polygons = polygons
        self.grids = grids

    def execute(self):
        for polygon, grid in zip(self.polygons, self.grids):
            print(polygon)
            for divsion in grid:
                print(divsion)
            
            print("--------------------")
