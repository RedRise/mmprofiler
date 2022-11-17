# MMPROFILER

Mangrove/Market Maker Profiler. This repo contains several usecases to run on a python terminal + one streamlit webapp ([available here](http://mmprofiler.deblaye.xyz/)).

## GitPod

[![Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/RedRise/mmprofiler)

## Local Setup

### Installation

1. Install Poetry
2. run ```poetry install```

### Module import issue

In case of module import issues, you may want to add a file (in the project root folder) named ```.env``` containing a single line:

PYTHONPATH=./

## Usage

### Usecases

See ```usecase_xx.py``` files for demos

### Streamlit

- ```poetry run streamlit run ./trajectory.py``` : call option hedging
