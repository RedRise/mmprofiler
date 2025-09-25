# Streamlit App Features Summary

This document summarizes the main features exposed by the Streamlit app (`trajectory.py`).

## Overview
The app provides interactive tools to explore market making strategies based on option delta curves, using both static and dynamic approaches. It leverages simulation, visualization, and analytics to help users understand the impact of different parameters and strategies.

## Main Features

### 1. Home Tab
- Introduction to market making with curves
- Explanation of static vs. dynamic delta curves
- Visual comparison of curve types

### 2. Single Path (Trajectory)
- Simulate asset price trajectory using geometric Brownian motion
- Adjustable parameters: number of days, intraday steps, seed, initial price, annual yield, volatility
- Visualize price evolution over time
- Mathematical background and Black-Scholes model explanation

### 3. Call Option
- Explore call option pricing and delta function (Black-Scholes)
- Adjustable parameters: maturity, strike, volatility, rate
- Visualize call price and delta curve
- 3D visualization of delta as a function of price and time to maturity

### 4. Maker
- Configure market maker parameters: static/dynamic delta, number of offers, tick interval
- Step through simulated time and apply arbitrage logic
- Visualize order book and maker's asset position
- Metrics: current/next price, delta, asset quantities
- Tabs for assets, transactions, snapshots, and debug state
- Interactive controls: next step, run to end, reset

### 5. Monte Carlo
- Run multiple market making simulations (Monte Carlo)
- Option to add long call position to PnL
- Detect and visualize linear trends in results
- Download simulation results as CSV
- Visualize asset and PnL distributions across simulations
- Context legend for parameter interpretation

## Technologies Used
- Streamlit for UI and interactivity
- Plotly for interactive charts
- Pandas and NumPy for data manipulation
- Scikit-learn and mlinsights for regression/trend analysis

## How to Use
- Launch with `streamlit run trajectory.py` or via Makefile (`make run`)
- Access the app at http://localhost:8501/
- Use the tabs and controls to explore different market making scenarios

## Typical Use Cases
- Visualize and compare market making strategies
- Analyze the impact of option parameters on delta curves
- Simulate and optimize maker behavior under different market conditions
- Run batch simulations to study PnL distributions and trends

---
For more details, see the code in `trajectory.py` or access the app live (see section )
