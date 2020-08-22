# Analyzing Counter-Strike: Global Offensive Data
The `csgo` package provides data parsing capabilities for Counter-Strike: Global Offensive (CSGO) data. In this repository, you will find the source code, issue tracker and useful information pertaining to the `csgo` package.

## Setup
### Requirements
`csgo` requires [Python](https://www.python.org/downloads/) >= 3.6 and [Golang](https://golang.org/dl/) >= 1.13. Python acts as a wrapper for the Go code which parses demofiles.

### Installation
To install `csgo`, clone the repository and install it from source by doing `python setup.py install`.

## Example Code
Using the `csgo` package is straightforward. Just pick a demofile and have a set of Pandas dataframes in seconds. Use the example below to get started.

```python
from csgo.parser import DemoParser

# Create parser object
# Set log=True above if you want to produce a logfile for the parser
demo_parser = DemoParser(demofile = "astralis-vs-liquid-m1-inferno.dem", match_id = "astralis-vs-liquid-m1-inferno.dem")


# Parse the demofile, output results to dictionary with df name as key
data = demo_parser.parse()
```

# The following keys exist
data["Map"]
data["Rounds"]
data["Damages"]
data["Kills"]
data["Bomb"]
data["Grenades"]
data["EnemiesFlashed"]
data["TeamFlashed"]
data["ItemPickup"]

## Examples
Take a look at the following Jupyter notebooks provided in our `examples/` directory.

- [Parsing a CSGO demofile and extract information](https://github.com/Paxoo/CSGODemo/tree/master/examples/gettingDemoInformation.ipynb)

## Structure
This repository contains code for CSGO analysis. It is structured as follows:

```
.
├── csgo
│   ├── analytics                 # Code for CSGO analysis
│   ├── data                      
│   │   ├── map                   # Map images
│   │   └── nav                   # Map navigation files
│   ├── parser                    # Code for CSGO demo parser
├── examples                      # Contains Jupyter Notebooks showing example code
```

## Requests and Issues
This project uses GitHub issues to track issues and feature requests.

## Acknowledgements
This project is made possible by the amazing work done in the [demoinfocs-golang](https://github.com/markus-wa/demoinfocs-golang) and [csgo](https://github.com/pnxenopoulos/csgo) packages. 

## License
Our project is licensed using the [MIT License](https://github.com/pnxenopoulos/csgo/blob/master/LICENSE).
=======
# Analyzing Counter-Strike: Global Offensive Data
The `csgo` package provides data parsing capabilities for Counter-Strike: Global Offensive (CSGO) data. In this repository, you will find the source code, issue tracker and useful information pertaining to the `csgo` package.

## Setup
### Requirements
`csgo` requires [Python](https://www.python.org/downloads/) >= 3.6 and [Golang](https://golang.org/dl/) >= 1.13. Python acts as a wrapper for the Go code which parses demofiles.

### Installation
To install `csgo`, clone the repository and install it from source by doing `python setup.py install`.

## Example Code
Using the `csgo` package is straightforward. Just pick a demofile and have a set of Pandas dataframes in seconds. Use the example below to get started.

```python
from csgo.parser import DemoParser

# Create parser object
# Set log=True above if you want to produce a logfile for the parser
demo_parser = DemoParser(demofile = "astralis-vs-liquid-m1-inferno.dem", match_id = "astralis-vs-liquid-m1-inferno.dem")


# Parse the demofile, output results to dictionary with df name as key
data = demo_parser.parse()
```

# The following keys exist
data["Map"]
data["Rounds"]
data["Damages"]
data["Kills"]
data["Bomb"]
data["Grenades"]
data["EnemiesFlashed"]
data["TeamFlashed"]
data["ItemPickup"]

## Examples
Take a look at the following Jupyter notebooks provided in our `examples/` directory.

- [Parsing a CSGO demofile and extract information](https://github.com/Paxoo/CSGODemo/examples/gettingDemoInformation.ipynb)

## Structure
This repository contains code for CSGO analysis. It is structured as follows:

```
.
├── csgo
│   ├── analytics                 # Code for CSGO analysis
│   ├── data                      
│   │   ├── map                   # Map images
│   │   └── nav                   # Map navigation files
│   ├── parser                    # Code for CSGO demo parser
├── examples                      # Contains Jupyter Notebooks showing example code
```

## Requests and Issues
This project uses GitHub issues to track issues and feature requests.

## Acknowledgements
This project is made possible by the amazing work done in the [demoinfocs-golang](https://github.com/markus-wa/demoinfocs-golang) and [csgo](https://github.com/pnxenopoulos/csgo) packages. 

## License
Our project is licensed using the [MIT License](https://github.com/pnxenopoulos/csgo/blob/master/LICENSE).
