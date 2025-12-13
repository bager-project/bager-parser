# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: GIS extractor

class GIS:
    """
        Extract .GIS entities and convert them into
        a Shapely elements.

        Attributes:
        path(str): path to the GIS file
    """
        
    def __init__(self, path):
        """
            Initialize all the variables.
        """

        self.path = path
        self.elements = []

    def execute(self):
        pass

    ###########################################################################
    #####                                                                 #####
    ###########################################################################

    def extract_entities(self):
        """
            Extract .GIS entities and convert them to
            Shapely geometry.
        """

        pass

    def get_elements(self):
        """
            Return Shapely elements.
        """

        return self.elements
