# B.A.G.E.R parser
This is project documentation parser for B.A.G.E.R.

Parser generates AST into binary file. Raspberry Pi Pico converts AST into actual motor sequences.

# B.A.G.E.R.
B.A.G.E.R. (Basic Autonomous Ground Excavation Robot) is an excavator featuring full project documentation parser. We are keen to keep human operators to oversee computers work. We are using Raspberry Pi Pico with C & C++ combination.

## Run instructions
- Install Python 3.10 or later
- Make virtual environment - `python -m venv bager-parser`
- Enter virtual environment - `source bager-parser/bin/activate`
    - If `source` is not found, install `virtualenv` pip package and run `virtualenv bager-parser/bin/activate`

- Install following packages:
    - [`colorama`](https://pypi.org/project/colorama/)
    - [`ezdxf`](https://pypi.org/project/ezdxf/)
    - [`matplotlib`](https://pypi.org/project/matplotlib/)
    - [`numpy`](https://pypi.org/project/numpy/)
    - [`shapely`](https://pypi.org/project/shapely/)
    - [`toml`](https://pypi.org/project/toml/)

    - *Just do `pip install [package]`*
- Go to `src` folder and run `python main.py`
