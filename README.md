# B.A.G.E.R. parser
This is a project documentation parser for B.A.G.E.R.

Parser parses project documentation which is either a CAD file, an image or a GIS file,
by extracting polygons and writing them to a file which is sent to Raspberry Pi Pico.

# B.A.G.E.R.
B.A.G.E.R. (Basic Autonomous Ground Excavation Robot) is an autonomous excavator robot featuring a full project documentation parser.
Parser is written in Python, while B.A.G.E.R.'s movement is controlled using Raspberry Pi Pico programmed with C and C++.
We are keen to keep human operators to oversee computer's work.

## Run instructions
- Install Python 3.10 or later.
- Make virtual environment - `python -m venv bager-parser`.
- Enter virtual environment - `source bager-parser/bin/activate` on Unix-like systems or `.\bager-parser\Scripts\activate ` on Windows.

| Install following packages                                 | Just do `pip install [package]`            |
| ---------------------------------------------------------- | ------------------------------------------ |
| [`colorama`](https://pypi.org/project/colorama/)           | [`ezdxf`](https://pypi.org/project/ezdxf/) |
| [`matplotlib`](https://pypi.org/project/matplotlib/)       | [`numpy`](https://pypi.org/project/numpy/) |
| [`opencv-python`](https://pypi.org/project/opencv-python/) | [`PyQt6`](https://pypi.org/project/PyQt6/) |
| [`shapely`](https://pypi.org/project/shapely/)             | [`toml`](https://pypi.org/project/toml/)   |

- Run the program from project directory `python src/main.py config.toml` or `python src/main-ui.py config.toml` if you want UI.

## Additional information
- [DOCUMENTATION](https://github.com/bager-project/bager-parser/blob/master/DOCUMENTATION.md)
- [TODO](https://github.com/ringwormGO-organization/bager-parser/blob/master/TODO.md)
