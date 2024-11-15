# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Lexer entry file

class Lexer:
    
    # Initialize all variables
    def __init__(self, grid):
        self.grid = grid

        self.test_grid()

    def test_grid(self):
        for i in range(len(self.grid)):
            print(self.grid[i])
