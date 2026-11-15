PYTHON ?= .venv/bin/python

all: process plots

data:
	$(PYTHON) src/download_data.py

process:
	$(PYTHON) -c "import sys; sys.path.insert(0,'src'); from pipeline import run; run()"

plots:
	$(PYTHON) src/visualize.py

notebook:
	$(PYTHON) -m jupyter notebook notebooks/01_end_to_end_colab.ipynb
