# B.A.G.E.R. parser documentation

This document features documentation on how to use config files.

## config.toml
This file contains all the necessary information for the parser to be able to parse the project documentation. Config file is divided into tables (sections) for easier organization. Each section MUST look like this:

```toml
[name_of_the_table]
    parser_type = "dxf" # dxf, image and GIS values are supported
    path = "dxf/two_rectangles_no_dimensions.dxf" # path to the file
    coords = [
        [
            [-100.0, 0.0],
            [0.0, 0.0],
            [0.0, 100.0],
        ],
        [
            [200.0, -100.0],
            [300.0, -100.0],
            [300.0, 0.0],
        ]
    ] # first level array holds arrays for each polygon, second level array holds arrays where an array is a coordinate of a single line; only first 3 points are enough to override, rest of points are automatically calculated

    depth = [100, 50] # depth of extracted polygons, an array for each polygon
    scale = 2.0 # scale coefficient for all polygons
    hole = true # are extracted polygons place to dig or dump soil
    debug = false # turn debug mode on
    grid_size = 25 # spacing between two lines in a grid (excluding breakpoints)
    min_spacing = 10.0 # minimum spacing between two lines in a grid (used when they are too many breakpoints, e.g. curved segments of a polygon)
```

As you see, polygons from the same file share certain properties (e.g. `hole` property).

## documentation.txt
Following design is applied:
```
SECTION_NAME-VALUE_OF_HOLE_VARIABLE
\tPOLYGON {i}
\t\tPOLYGON Z((0 0 100, 100 0 100, 100 100 100, 0 100 100))
```

In embedder polygons are divided into smaller polygons based on line divisions. We just group them here for the sake of easier organization.
