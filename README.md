<img src="logo/logo1.jpg" width="300" title="holochat logo" alt="holochat logo" align="right" vspace = "50">

# HoloChat Server


A "modern" stim message server to facilitate communication between rig computers. 

![ci workflow](https://github.com/willyh101/holochat/actions/workflows/main.yml/badge.svg)
[![codecov](https://codecov.io/gh/willyh101/holochat/graph/badge.svg?token=VB8RWD9Z31)](https://codecov.io/gh/willyh101/holochat)
## Installation

### Easy mode install

Just install and call from the commandline without cloning the repo.

```bash
conda create -n holochat python pip
conda activate holochat
pip install git+https://github.com/willyh101/holochat.git
```

Then you can immediately run the server with `holochat run`.


### Install via venv and pip

If you have a python >3.10 on your system, you can install the package directly from github and use venv. I'm assuming you've already cloned the repo.
    
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

### Install via conda

You can also install using conda/mamba to manage python. Just install the most recent python version, whatever version comes up (that's >=3.10).

```bash
conda create -n holochat python pip
conda activate holochat
pip install -e '.[dev]'
```

## Usage

### Settings File

The settings file is a json file that contains generic settings for the server.

Settings can live in either the project directory or in the user's home directory. The settings file in the user's home directory will take precedence over the one in the repo directory.

In order to generate the settings file, run `holochat setup`. This generates the settings file in the repo. If you want it in your home directory, use `holochat setup --home`. To overwrite the settings file in your home directory (or in the repo) use `--ow` flag.

### Running the server

`holochat run`, the server will load the settings file automatically and run. If this gives you trouble, try `python -m holochat`

API documentation (aka GET, POST, DELETE) is available at `http://[your-local-ip]:8000/docs`.
