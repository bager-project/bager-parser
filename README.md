# B.A.G.E.R. parser
This is a project documentation parser for B.A.G.E.R.

Parser parses project documentation which is either a CAD file, an image or a GIS file,
by extracting polygons and writing them to a file which is sent to Raspberry Pi Pico.

# B.A.G.E.R.
B.A.G.E.R. (Basic Autonomous Ground Excavation Robot) is an autonomous excavator robot featuring a full project documentation parser.
Parser is written in Python, while B.A.G.E.R.'s movement is controlled using Raspberry Pi Pico programmed with C and C++.
We are keen to keep human operators to oversee computer's work.

## TODO
- [TODO](https://github.com/ringwormGO-organization/bager-parser/blob/master/TODO.md)

## Run instructions
- Install Python 3.10 or later
- Make virtual environment - `python -m venv bager-parser`
- Enter virtual environment - `source bager-parser/bin/activate`

  - If `source` is not found, install `virtualenv` pip package and run `virtualenv bager-parser/bin/activate`

| Install following packages                                 | Just do `pip install [package]`            |
| ---------------------------------------------------------- | ------------------------------------------ |
| [`colorama`](https://pypi.org/project/colorama/)           | [`ezdxf`](https://pypi.org/project/ezdxf/) |
| [`matplotlib`](https://pypi.org/project/matplotlib/)       | [`numpy`](https://pypi.org/project/numpy/) |
| [`opencv-python`](https://pypi.org/project/opencv-python/) | [`PyQt6`](https://pypi.org/project/PyQt6/) |
| [`shapely`](https://pypi.org/project/shapely/)             | [`toml`](https://pypi.org/project/toml/)   |

- Run the program from project directory `python src/main.py config.toml`
