# DNA Fiber Analysis

A Python pipeline for automated analysis of DNA fiber assay measurements exported from ImageJ/Fiji.

The project aggregates measurements from multiple experiments, converts fiber lengths into physical units, calculates replication parameters, performs statistical analysis, and generates publication-quality figures.

---

## Features

- Import measurements from multiple CSV files
- Aggregate data from nested directories
- Convert fiber lengths from pixels to micrometers
- Calculate:
  - Replication fork speed (kb/min)
  - Inter-origin distance (kb)
- Automatic sample and ROI annotation
- Mann–Whitney U statistical comparisons
- Publication-quality boxplots with significance annotations
- Export summary statistics to Excel

---

## Project structure

```
DNA_fibers/
│
├── preprocess.py           # The Jython script to run inside ImageJ/FIJI for multichannel imgs preprocessing
├── manual_measure.py       # The Jython script to run inside ImageJ/FIJI to generate measurements
├── notebook_stats.ipynb    # Main analysis notebook
├── utils.py                # Data loading and helper functions for notebook
├── plotting.py             # Helper functions for notebook to make plots
├── requirements
└── README.md
```

---

## Requirements

Python 3.10+

Required packages:

```bash
pip install pandas numpy scipy matplotlib openpyxl
```

or

```bash
pip install -r requirements.txt
```

---

## Input data

The pipeline expects CSV files exported from ImageJ/Fiji.

Example directory structure:

```
input/
├── WT/
│   ├── WT_01.csv
│   └── WT_02.csv
│   └── ...
├── siSCR/
│   ├── siSCR_01.csv
│   └── siSCR_02.csv
│   └── ...
├── siORC1/
│   ├── siORC1_01.csv
│   └── siORC1_02.csv
│   └── ...
└── ...
```

The CSV files should contain measurements including:

- Label
- Length
- Measurement_type

---

## Workflow

1. Run `manual_measure.py` script for Fiji/ImageJ to create the measurements of Inter-origin distance and fiber length.
2. Set the pixel size and experimental parameters in `notebook_stats.ipynb`.
3. Run the notebook from top to bottom.
4. The notebook will:
   - load all measurements,
   - calculate replication parameters,
   - perform statistical analysis,
   - generate figures,
   - export tables.

---

## Output

The pipeline generates:

- aggregated datasets
- replication fork speed tables
- inter-origin distance tables
- statistical comparisons
- publication-quality figures

---


## Citation

If you use this code in your research, please cite the associated publication (when available).

---

## Author

Elena Lopatukhina