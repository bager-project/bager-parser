# AUTHOR Andrej Bartulin, EndermanPC
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: .dxf extractor

import ezdxf
import math
import os
import numpy as np
from shapely.geometry import LineString, Point, Polygon

class DXF:
    """
        Extract .dxf entities and convert them into
        a Shapely element.

        Attributes:
        path(str): path to the .dxf file
    """

    def __init__(self, path):
        """
            Initialize all the variables.
        """

        self.path = path
        self.elements = []

        if not os.path.exists(path):
            print(f"File in path '{path}' does not exist!")
            print("Exiting...")

            exit(0)

        self.doc = ezdxf.readfile(self.path)
        self.modelspace = self.doc.modelspace()

    def execute(self):
        self.extract_entities()

    ###########################################################################
    #####                                                                 #####
    ###########################################################################

    def extract_entities(self):
        """
            Extract .dxf entities and convert them to
            Shapely geometry.
        """

        for entity in self.modelspace:
            match entity.dxftype():
                case 'ARC':
                    center = (entity.dxf.center.x, entity.dxf.center.y)
                    radius = entity.dxf.radius
                    start_angle = entity.dxf.start_angle
                    end_angle = entity.dxf.end_angle

                    arc = self.arc_to_linestring(center, radius, start_angle, end_angle)
                    self.elements.append(arc)

                case 'CIRCLE':
                    center = (entity.dxf.center.x, entity.dxf.center.y)
                    radius = entity.dxf.radius
                    
                    circle = Point(center).buffer(radius, resolution=64)
                    self.elements.append(circle)

                case 'ELLIPSE':
                    center = (entity.dxf.center.x, entity.dxf.center.y)
                    major_axis = np.array([entity.dxf.major_axis.x, entity.dxf.major_axis.y])
                    ratio = entity.dxf.ratio
                    start_param = entity.dxf.start_param
                    end_param = entity.dxf.end_param
                    extrusion = np.array([entity.dxf.extrusion.x, entity.dxf.extrusion.y, entity.dxf.extrusion.z])

                    # Calculate the length of the major axis (magnitude of the major_axis vector)
                    major_axis_length = np.linalg.norm(major_axis)

                    # Calculate the minor axis by taking the cross product of extrusion and major_axis
                    minor_axis = np.cross(extrusion, major_axis)
                    minor_axis_length = np.linalg.norm(minor_axis)
                    minor_axis = minor_axis / minor_axis_length * major_axis_length * ratio

                    ellipse = self.create_ellipse(center, major_axis, minor_axis, start_param, end_param)
                    self.elements.append(ellipse)

                case 'LINE':
                    start_point = (entity.dxf.start.x, entity.dxf.start.y)
                    end_point = (entity.dxf.end.x, entity.dxf.end.y)

                    self.elements.append(LineString([start_point, end_point]))

                case 'LWPOLYLINE':
                    points = [(point[0], point[1]) for point in entity]
                    self.elements.append(LineString(points))

                case 'SPLINE':
                    control_points = [(p[0], p[1]) for p in entity.control_points]
                    spline_line = LineString(control_points)

                    self.elements.append(spline_line)

                case 'DIMENSION':
                    pass

                case _:
                    pass

    def get_elements(self):
        """
            Return Shapely elements.
        """

        return self.elements
    
    ###########################################################################
    #####                                                                 #####
    ###########################################################################

    def arc_to_linestring(self, center, radius, start_angle, end_angle, num_segments=64):
        """
            INTERNAL FUNCTION!

            Convert a .dxf ARC entity into a Shapely LineString.
        """
        
        # Convert start and end angles from degrees to radians
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        
        # Handle cases where the arc crosses the 0-degree line
        if end_rad < start_rad:
            end_rad += 2 * math.pi
        
        # Generate points along the arc using a linear space of angles
        angles = np.linspace(start_rad, end_rad, num_segments)
        points = [(center[0] + radius * math.cos(theta), center[1] + radius * math.sin(theta)) for theta in angles]
        
        return LineString(points)

    def create_ellipse(self, center, major_axis, minor_axis, start_param, end_param, resolution=64):
        """
            INTERNAL FUNCTION!

            Convert .dxf ELLIPSE entity into a Shapely Polygon
        """
        
        # Parametric equations for an ellipse
        theta = np.linspace(start_param, end_param, resolution)
        x = center[0] + major_axis[0] * np.cos(theta) + minor_axis[0] * np.sin(theta)
        y = center[1] + major_axis[1] * np.cos(theta) + minor_axis[1] * np.sin(theta)

        # Create the polygon approximation of the ellipse
        points = list(zip(x, y))
        return Polygon(points)
