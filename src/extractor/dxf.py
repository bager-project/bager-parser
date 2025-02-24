# AUTHOR Andrej Bartulin, EndermanPC
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: .dxf extractor entry file

import ezdxf
import math
import numpy as np
import os
from shapely.geometry import LineString, Point, Polygon

def arc_to_linestring(center, radius, start_angle, end_angle, num_segments=64):
    """
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

def create_ellipse(center, major_axis, minor_axis, start_param, end_param, resolution=64):
    """
        Convert .dxf ELLIPSE entity into a Shapely Polygon
    """
    
    # Parametric equations for an ellipse
    theta = np.linspace(start_param, end_param, resolution)
    x = center[0] + major_axis[0] * np.cos(theta) + minor_axis[0] * np.sin(theta)
    y = center[1] + major_axis[1] * np.cos(theta) + minor_axis[1] * np.sin(theta)

    # Create the polygon approximation of the ellipse
    points = list(zip(x, y))
    return Polygon(points)

class DXF:
    """
        Class extracting .dxf entities and converting them into
        a form of Shapely class.

        Attributes:
        path(str): path to the .dxf file
    """

    def __init__(self, path) -> None:
        """
            Initialize all the variables.
        """

        self.path = path
    
        # Dictionary to store all extracted Shapely elements
        # https://ezdxf.readthedocs.io/en/stable/dxfentities/index.html
        self.elements = {
            'ARC': [],
            'ATTRIB': [],
            'BODY': [],
            'CIRCLE': [],
            'DIMENSION': [],
            'ARC_DIMENSION': [],
            'ELLIPSE': [],
            'HATCH': [],
            'HELIX': [],
            'IMAGE': [],
            'INSERT': [],
            'LEADER': [],
            'LINE': [],
            'LWPOLYLINE': [],
            'MLINE': [],
            'MESH': [],
            'MPOLYGON': [],
            'MTEXT': [],
            'MULTILEADER': [],
            'POINT': [],
            'POINTS': [], # this is for image extractor
            'POLYLINE': [],
            'VERTEX': [],
            'RAY': [],
            'REGION': [],
            'SHAPE': [],
            'SOLID': [],
            'SPLINE': [],
            'SURFACE': [],
            'TEXT': [],
            'TRACE': [],
            'VIEWPORT': [],
            'WIPEOUT': [],
            'XLINE': [],
            'UNIMPLEMENTED': [],
        }

        if not os.path.exists(path):
            print(f"File in path {path} does not exist!")
            print("Exiting...")

            exit(0)

        self.doc = ezdxf.readfile(path)
        self.modelspace = self.doc.modelspace()

        self.extract_entities()

    def get_elements(self):
        """
            Return the dictionary containing all detected
            .dxf elements.
        """

        return self.elements

    def extract_entities(self) -> None:
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

                    arc = arc_to_linestring(center, radius, start_angle, end_angle)
                    self.elements['ARC'].append(arc)

                case 'CIRCLE':
                    center = (entity.dxf.center.x, entity.dxf.center.y)
                    radius = entity.dxf.radius
                    
                    circle = Point(center).buffer(radius, resolution=64)
                    self.elements['CIRCLE'].append(circle)

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

                    ellipse = create_ellipse(center, major_axis, minor_axis, start_param, end_param)
                    self.elements['ELLIPSE'].append(ellipse)

                case 'DIMENSION':
                    self.elements['DIMENSION'].append(entity)

                case 'LINE':
                    start_point = (entity.dxf.start.x, entity.dxf.start.y)
                    end_point = (entity.dxf.end.x, entity.dxf.end.y)

                    self.elements['LINE'].append(LineString([start_point, end_point]))

                case 'LWPOLYLINE':
                    points = [(point[0], point[1]) for point in entity]
                    self.elements['LWPOLYLINE'].append(LineString(points))

                case 'SPLINE':
                    control_points = [(p[0], p[1]) for p in entity.control_points]
                    spline_line = LineString(control_points)

                    self.elements['SPLINE'].append(spline_line)

                case _:
                    self.elements['UNIMPLEMENTED'].append(entity)

    # Print found entities
    def print_entities(self) -> None:
        """
            DEBUG FUNCTION!

            Print extracted .dxf entities.
        """

        for element_type, entities in self.elements.items():
            print(f"{element_type}: {len(entities)} entities found")
            for entity in entities:
                print(entity)
