# Business License Registration Analysis

## Overview
This project analyzes business license registration data from Vancouver. It contains a dataset with 131,742 business licenses and provides tools for data exploration and analysis.

## Project Structure
- `business-licences.csv` - Main dataset with business license information (34MB)
- `main.py` - Python script for basic data exploration
- `analysis.ipynb` - Jupyter notebook for interactive analysis
- `pyproject.toml` - Python project configuration
- `uv.lock` - Dependency lock file

## Dataset Information
The dataset contains the following key columns:
- Business information (name, trade name, type, subtype)
- Location data (address, city, postal code, coordinates)
- License details (number, status, issued/expired dates)
- Other metadata (employees, fees, local area)

Total records: 131,742 business licenses

## Installed Libraries
- **pandas** - Data manipulation and analysis
- **matplotlib** - Data visualization
- **seaborn** - Statistical visualization
- **numpy** - Numerical computing
- **scipy** - Scientific computing
- **jupyter** - Interactive notebooks
- **ipykernel** - Jupyter kernel for Python

## How to Use

### Running the Python Script
The main.py script provides a quick overview of the dataset:
```bash
python main.py
```

### Using Jupyter Notebook
For interactive analysis, use the analysis.ipynb notebook which includes:
- Data loading and exploration
- Missing value analysis
- Basic statistics
- Template cells for custom analysis

## Recent Changes
- **2025-11-10**: Initial setup with Python data analysis environment
- Installed pandas, matplotlib, seaborn, numpy, scipy, jupyter
- Added business-licences.csv dataset (131,742 records)
- Created basic analysis scripts and Jupyter notebook

## User Preferences
- Language: Python 3.11
- Environment: Replit with UV package manager
- Analysis tools: pandas, matplotlib, seaborn

## Notes
- The CSV file uses semicolon (;) as delimiter
- Geographic data is included in GeoJSON format
- Dataset extracted on 2025-11-01
