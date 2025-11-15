# Simple GUI program for drug stock management

A modern web-based application for hospital drug stock management built with Dash and Bootstrap.

# User guide
A minimal user guide is available [here](https://github.com/francescocarpanese/stock_management/wiki).

# Installation

## Developer

- Install `uv` [here](https://docs.astral.sh/uv/)

- Clone the repository

- Install dependencies
```bash
cd stock_management
uv sync
```

- Run the web application
```bash
uv run stock-management
```

The application will be available at http://127.0.0.1:8050

## Production
To compile the app with a .exe 
```bash
uv run pyinstaller main.spec
```