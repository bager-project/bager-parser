# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: GIS extractor

import os

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

        if not os.path.exists(path):
            print(f"[EXTRACTOR-GIS] File in path '{path}' does not exist!")
            print("[EXTRACTOR-GIS] Exiting...")

            exit(0)

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
