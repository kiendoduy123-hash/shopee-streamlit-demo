# Shopee Clone MVP

A minimalist clone of an e-commerce platform built with Streamlit and managed with `uv`. 
It implements a complete core shopping loop: viewing products, managing a cart, and checking out.

## Instructions to Run 🚀

### 1. Install uv
If you haven't installed `uv` yet, you can do so by running:

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Run the Streamlit Application
We use `uv run` to automatically resolve dependencies defined in `pyproject.toml`, build a virtual environment locally if needed, and execute the Streamlit app.

Navigate to this directory in your terminal and run:

```bash
uv run streamlit run app.py
```

`uv` is extremely fast and will instantly install `streamlit` & `pandas` the first time you execute the command, and subsequently boot up the UI.
