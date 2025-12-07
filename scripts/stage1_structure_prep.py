#!/usr/bin/env python3.11
"""
Stage 1: Structure Preparation
Downloads PDB 2ZZF and prepares it for analysis
"""

import os
import sys
from pathlib import Path
from Bio.PDB import PDBParser, PDBIO, Select

BASE_DIR = Path("/home/ubuntu/alars_validation")
STRUCTURES_DIR = BASE_DIR / "structures"

class ProteinOnlySelect(Select):
    """Select only protein atoms (no water, ligands)"""
    def accept_residue(self, residue):
        return residue.id[0] == " "

def download_pdb(pdb_id):
    """Download PDB structure"""
    print(f"[1/3] Downloading PDB {pdb_id}...")
    pdb_file = STRUCTURES_DIR / f"{pdb_id}.pdb"
    
    if pdb_file.exists():
        print(f"  ✓ Already exists: {pdb_file}")
        return pdb_file
    
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    os.system(f"wget -q -O {pdb_file} {url}")
    
    if pdb_file.exists():
        print(f"  ✓ Downloaded: {pdb_file}")
        return pdb_file
    else:
        raise FileNotFoundError(f"Failed to download {pdb_id}")

def clean_structure(pdb_file, chain="A"):
    """Extract protein chain and remove heteroatoms"""
    print(f"[2/3] Cleaning structure (chain {chain})...")
    
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("alars", pdb_file)
    
    # Save clean protein
    clean_file = STRUCTURES_DIR / f"{pdb_file.stem}_clean.pdb"
    io = PDBIO()
    io.set_structure(structure)
    io.save(str(clean_file), select=ProteinOnlySelect())
    
    print(f"  ✓ Clean structure: {clean_file}")
    return clean_file

def analyze_structure(pdb_file):
    """Analyze structure and find Ala binding site"""
    print(f"[3/3] Analyzing structure...")
    
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("alars", pdb_file)
    
    # Count residues
    residues = [r for r in structure.get_residues() if r.id[0] == " "]
    print(f"  ✓ Total residues: {len(residues)}")
    
    # Find key residues
    key_residues = [192, 193, 213, 215, 217, 249]
    found = {}
    
    for res in residues:
        if res.id[1] in key_residues:
            found[res.id[1]] = res.resname
    
    print(f"  ✓ Key residues found:")
    for pos, resname in sorted(found.items()):
        print(f"      Position {pos}: {resname}")
    
    return found

def main():
    print("\n" + "="*70)
    print("  Stage 1: Structure Preparation")
    print("="*70 + "\n")
    
    # Create directories
    STRUCTURES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Download and process
    pdb_file = download_pdb("2ZZF")
    clean_file = clean_structure(pdb_file)
    residues = analyze_structure(clean_file)
    
    print("\n" + "-"*70)
    print("✓ Stage 1 Complete")
    print("-"*70)
    print(f"Output: {clean_file}")
    
    return clean_file

if __name__ == "__main__":
    main()
