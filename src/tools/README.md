# Tools

Agent tools for data loading, visualization, and documentation access.

## Available Tools

### `data_loader_tool.py`
Loads order data from CSV files between specified date ranges. Returns pandas DataFrame for analysis.

**Input**: `"YYYY-MM-DD, YYYY-MM-DD"` (start date, end date)

### `data_vizualization_tool.py`
Generates charts and visualizations using matplotlib/plotly. Saves images to static directory for display.

**Supports**: Bar charts, line plots, pie charts, scatter plots, heatmaps

### `data_documentation_tool.py`
Provides access to data schema documentation from `data_documentation.yaml`. Helps agents understand available columns and data types.

### `json_tools.py`
Utilities for working with JSON data and structured outputs.

## Usage

Tools are registered with agents during initialization and invoked automatically based on query requirements.
