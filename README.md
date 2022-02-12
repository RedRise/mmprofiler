# MMPROFILER

Mangrove Maker Profiler

## Usage

See ```usecase_xx.py``` files for demos.

## Install Conda env with required dependencies

```conda env create -n your_env_name -f mmmprofiler_deps.yaml -v python=3.9```


## Module import issue

In case of module import issues, you may want to add a file (in the project root folder) named ```.env``` containing a single line:

PYTHONPATH=./
