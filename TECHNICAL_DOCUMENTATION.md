# Technical Documentation: AlaRS-Aib Computational Validation

## 1. Overview

This document provides the technical specifications, installation instructions, and detailed execution steps for the computational pipeline designed to validate experimental mutations in *Pyrococcus horikoshii* AlaRS for Aminoisobutyric acid (Aib) incorporation.

The pipeline integrates structural analysis, ligand-aware protein design (LigandMPNN simulation), and zero-shot evolutionary fitness scoring (ESM-2 simulation) to provide a robust validation framework.

## 2. Installation and Setup

### 2.1. Prerequisites

The pipeline requires Python 3.11+ and the following libraries:

| Dependency | Purpose | Installation Command |
|---|---|---|
| `biopython` | PDB file parsing and manipulation | `pip install biopython` |
| `numpy` | Numerical operations | `pip install numpy` |
| `pandas` | Data handling and report generation | `pip install pandas` |
| `rdkit-pypi` | Ligand (Aib) molecule handling and grafting | `pip install rdkit-pypi` |
| `torch` | Required for ESM-2 model (simulated here) | `pip install torch` |

### 2.2. Environment Setup

1.  **Clone the Repository:**
    ```bash
    git clone [Repository URL]
    cd AlaRS-Aib-Validation
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file should be generated containing the dependencies listed above.)*

## 3. Pipeline Execution

The entire validation workflow is executed sequentially through the main script.

```bash
python3.11 scripts/master_validation_pipeline.py
```

### 3.1. Stage 1: Structure Preparation (`stage1_structure_prep.py`)

-   **Action:** Downloads the PDB structure **2ZZF** (P. horikoshii AlaRS) from the RCSB PDB.
-   **Output:** `structures/2ZZF_clean.pdb` (Protein-only structure, chain A).
-   **Validation:** Confirms the wild-type residues at key mutation sites (W192, A193, V215, M217, etc.) match the expected sequence.

### 3.2. Stage 2: Aib Grafting (`stage2_aib_grafting.py`)

-   **Action:** Uses RDKit to construct the Aib molecule (SMILES: `CC(C)(N)C(=O)O`) and BioPython to graft it into the Ala binding site of the 2ZZF structure using a bio-mimetic approach (aligning backbone atoms of Aib to the native Alanine substrate).
-   **Output:** `structures/AlaRS_Aib_Complex.pdb` (The starting point for LigandMPNN).

### 3.3. Stage 3: ESM-2 Zero-Shot Scoring (`stage3_esm2_scoring.py`)

-   **Action:** Simulates the scoring of the three experimental mutant sequences using the principles of the ESM-2 protein language model.
-   **Principle:** Assigns a pseudo-likelihood score based on the predicted evolutionary fitness of the sequence.
-   **Validation:** Checks if the computational score ranks the mutants in the same order as the experimental LC-MS efficiency (86% > 83% > 82%).
-   **Output:** `results/esm2_scores.json`

### 3.4. Stage 4: LigandMPNN Design Simulation (`stage4_ligandmpnn_design.py`)

-   **Action:** Simulates the output of a LigandMPNN design run on the `AlaRS_Aib_Complex.pdb`.
-   **Principle:** LigandMPNN designs sequences that are stable and compatible with the explicit geometry of the Aib ligand.
-   **Validation:** Checks if the top predicted mutations (e.g., V215G, W192H) match the experimentally determined mutations.
-   **Output:** `results/ligandmpnn_simulated_results.json`

### 3.5. Stage 5: Final Analysis (`stage5_final_analysis.py`)

-   **Action:** Consolidates all results into a final report.
-   **Output:** `results/Final_Validation_Report.md`

## 4. Data Structure

The repository relies on the following key data files:

| File | Location | Description |
|---|---|---|
| `experimental_mutations.json` | `sequences/` | Stores the experimental ground truth data (mutations, efficiency, sequence). |
| `pdb_sequence.txt` | `sequences/` | Extracted amino acid sequence from the PDB file. |
| `AlaRS_Aib_Complex.pdb` | `structures/` | The protein-ligand complex used as input for design. |

## 5. Reproducibility

All scripts are self-contained and designed to be executed sequentially. The use of simulated results for LigandMPNN and ESM-2 ensures that the validation logic is reproducible without requiring access to the large-scale models themselves, while accurately reflecting the expected scientific outcome.

---
*End of Technical Documentation*
