# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Lexer entry file

class Lexer:
    """
        Tokenize every polygon division.

        Attributes:
            polygons(list): list of polygons
            divisions(list): list of lines (divisions) FOR EACH polygon
    """

    def __init__(self, polygons, divisions):
        """
            Initialize all the variables.
        """

        self.polygons = polygons
        self.divisions = divisions

    def execute(self):
        """
            Tokenize.
        """
        
        for polygon, division in zip(self.polygons, self.divisions):
            print("--- SHAPE ----: ")
            print(polygon)

            print("--- DIVISIONS ---: ")
            for line in division:
                print(line)
            
            print("----------------------------------------")
