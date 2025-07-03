# B.A.G.E.R. parser documentation

This document features documentation on how to use config files.

## config.toml
This file contains all the necessary information for parser to be able to parse the project documentation. Config file is divided into tables (sections) for easier organization. Each section MUST look like this:

```toml
[name_of_the_table]
    parser_type = "dxf" # dxf, image and GIS values are supported
    path = "dxf/circle_dimensions.dxf" # path to the file
    position_path = "none" # if you want to override position from the file
    depth = [100, 50] # depth of extracted polygons
    hole = true # are extracted polygons place to dig or dump soil
```

As you see, amongst polygons from the same file, they share certain properties (e.g. `hole` property).

## position.toml
Currently only GPS coordinates are supported. Therefore, everything has to be under `[gps]` table. Position defining is done by creating an array of arrays of arrays.

First array which MUST be called `polygon_coords`. For each extracted polygon there is an array. Final array is an array of AT LEAST 3 consecutive new coordinates. Rest of the coordinates will be automatically calculated.

Example:
```toml
[gps]
polygon_coords = [
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
]
```

## documentation.txt
Following design is applied:
```
SECTION_NAME-VALUE_OF_HOLE_VARIABLE
\tPOLYGON {i}
\t\tPOLYGON Z((0 0 100, 100 0 100, 100 100 100, 0 100 100))
```

In embedder polygons are divided into smaller polygons based on line divisions. We just group them here for the sake of easier organization.
