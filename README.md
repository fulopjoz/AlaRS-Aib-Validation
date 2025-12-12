# AlaRS-Aib-Validation: Computational Validation of Engineered tRNA Synthetase

## Overview

This repository contains the computational pipeline for validating experimental mutations in **Pyrococcus horikoshii Alanyl-tRNA Synthetase (AlaRS)** designed to incorporate **Aminoisobutyric acid (Aib)**.

The approach follows ChemInformatics best practices, combining **LigandMPNN** (for ligand-aware design) and **ESM-2** (for evolutionary fitness scoring) to provide a robust, predictive framework.

## Documentation

The project is documented across three files to serve different audiences:

1.  **[SCIENTIFIC_REPORT.md](SCIENTIFIC_REPORT.md)**: A comprehensive, publication-style report detailing the scientific methodology, results, discussion, and full citations. *Targeted at scientific collaborators and researchers.*
2.  **[TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)**: Detailed instructions on installation, environment setup, script-by-script execution, and data structure. *Targeted at developers and computational scientists.*
3.  **README.md** (This file): A brief overview and entry point to the project.

## Key Findings

The computational pipeline successfully validated the experimental results:

*   **LigandMPNN** predicted the critical **V215G** and **W192H** mutations.
*   **ESM-2** zero-shot scoring **perfectly correlated** with the experimental incorporation efficiency (86% > 83% > 82%).

## Repository Structure

```
alars_validation/
├── docs/
├── results/
├── scripts/
├── sequences/
├── structures/
├── README.md
├── TECHNICAL_DOCUMENTATION.md
└── SCIENTIFIC_REPORT.md
```

## Usage

To run the full validation pipeline:

```bash
python3.11 scripts/master_validation_pipeline.py
```

---
*Full code and data available on GitHub: [Repository URL]*
