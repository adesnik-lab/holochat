# StimSync Server

A "modern" stim message server to facilitate communication between rig computers.

## Installation

### Install via venv and pip

If you have a python >3.10 on your system, you can install the package directly from github and use venv. I'm assuming you've already cloned the repo.
    
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Install via conda

You can also install using conda/mamba to manage python. Just install the most recent python version, whatever version comes up (that's >=3.10).

```bash
conda create -n stimsync python pip
conda activate stimsync
pip install -e .
```

## Usage

### Config file

There's a config file (config.json) that you can edit to change the default settings. They have all the default values filled in, so overwrite what you want to change.

### Running the server