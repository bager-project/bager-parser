# AUTHOR Andrej Bartulin, EndermanPC
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: .dxf extractor entry file

import ezdxf
import numpy as np
import os
from shapely.geometry import LineString, Point, Polygon

# Helper function to create an ellipse as Shapely polygon
def create_ellipse(center, major_axis, minor_axis, start_param, end_param, resolution=64):
    # Parametric equations for an ellipse
    theta = np.linspace(start_param, end_param, resolution)
    x = center[0] + major_axis[0] * np.cos(theta) + minor_axis[0] * np.sin(theta)
    y = center[1] + major_axis[1] * np.cos(theta) + minor_axis[1] * np.sin(theta)

    # Create the polygon approximation of the ellipse
    points = list(zip(x, y))
    return Polygon(points)

# DXF parser
class DXF:

    # Initialize all variables
    def __init__(self, path) -> None:
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

    # Run parser
    def get_elements(self):
        return self.elements

    # Extract .dxf entities and convert them to Shapely geometry
    def extract_entities(self) -> None:
        # Extract different types of elements
        for entity in self.modelspace:
            match entity.dxftype():
                case 'CIRCLE':
                    center = (entity.dxf.center.x, entity.dxf.center.y)
                    radius = entity.dxf.radius
                    
                    circle = Point(center).buffer(radius, resolution=64)
                    self.elements['CIRCLE'].append(circle)

                case 'ELLIPSE':
                    # Extract ellipse parameters
                    center = (entity.dxf.center.x, entity.dxf.center.y)
                    major_axis = np.array([entity.dxf.major_axis.x, entity.dxf.major_axis.y])  # Major axis vector
                    ratio = entity.dxf.ratio  # Ratio of minor to major axis
                    start_param = entity.dxf.start_param  # Start param (angle in radians)
                    end_param = entity.dxf.end_param  # End param (angle in radians)
                    extrusion = np.array([entity.dxf.extrusion.x, entity.dxf.extrusion.y, entity.dxf.extrusion.z])  # Normal vector to the ellipse plane

                    # Calculate the length of the major axis (magnitude of the major_axis vector)
                    major_axis_length = np.linalg.norm(major_axis)

                    # Calculate the minor axis by taking the cross product of extrusion and major_axis
                    minor_axis = np.cross(extrusion, major_axis)
                    minor_axis_length = np.linalg.norm(minor_axis)
                    minor_axis = minor_axis / minor_axis_length * major_axis_length * ratio  # Scale to the minor axis length

                    # Create ellipse as Shapely geometry
                    ellipse = create_ellipse(center, major_axis, minor_axis, start_param, end_param)
                    self.elements['ELLIPSE'].append(ellipse)

                case 'LINE':
                    start_point = (entity.dxf.start.x, entity.dxf.start.y)
                    end_point = (entity.dxf.end.x, entity.dxf.end.y)

                    self.elements['LINE'].append(LineString([start_point, end_point]))

                case 'LWPOLYLINE':
                    points = [(point[0], point[1]) for point in entity]
                    self.elements['LWPOLYLINE'].append(LineString(points))

                case 'DIMENSION':
                    self.elements['DIMENSION'].append(entity)

                case _:
                    self.elements['UNIMPLEMENTED'].append(entity)

    # Print found entities
    def print_entities(self) -> None:
        # Extract different types of elements
        for element_type, entities in self.elements.items():
            print(f"{element_type}: {len(entities)} entities found")
            for entity in entities:
                print(entity)
