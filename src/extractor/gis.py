# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: GIS extractor

class GIS:
    """
        Extract GIS entities and convert them into Shapely elements.

        :param str path: path to the GIS file
    """

    def __init__(self, path):
        """
            Initialize variables.
        """

        self.path = path
        self.elements = []

    def execute(self):
        """
            Extract.
        """

        self.extract_entities()

    ###########################################################################
    #####                                                                 #####
    ###########################################################################

    def extract_entities(self):
        """
            Extract GIS entities and convert them into Shapely geometry.
        """

        pass

    def get_elements(self):
        """
            Return Shapely elements.
        """

        return self.elements
