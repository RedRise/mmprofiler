
# MMPROFILER

[![Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/RedRise/mmprofiler)

Mangrove/Market Maker Profiler. This repository contains several use cases to run in a Python terminal, plus a Streamlit webapp.

For a detailed summary of the Streamlit app features, see [README_STREAMLIT.md](README_STREAMLIT.md).

## Market Making exploration webapp

The app provides interactive tools to explore market making strategies based on option delta curves, using both static and dynamic approaches. It leverages simulation, visualization, and analytics to help users understand the impact of different parameters and strategies.

### Main Features

- Visualization of orders and order book
- Simulate taking positions (buy/sell at best price)
- Analyze market maker PnL across different price ranges
- Simulate price diffusion (geometric Brownian motion)
- Interactive results and charts (Plotly)
- Compare different market making strategies (Zero Knowledge, Delta, Replication)


## Local Setup

### Installation

  1. [Install Poetry](https://python-poetry.org/docs/#installation)
  2. Run: ```poetry install```
  3. Or use the Makefile: ```make install```

#### Run the Streamlit Web App

  1. Run: ```poetry run streamlit run ./trajectory.py```
  2. Or use the Makefile: ```make run```
  3. Access the app at [http://localhost:8501/](http://localhost:8501/)
