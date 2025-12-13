#!/usr/bin/env python3.11
"""
Stage 2: Aib Grafting
Grafts Aib molecule into the Ala binding site using bio-mimetic approach
"""

import os
import sys
import numpy as np
from pathlib import Path
from Bio.PDB import PDBParser, PDBIO, Select
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Geometry import Point3D

BASE_DIR = Path("/home/ubuntu/alars_validation")
STRUCTURES_DIR = BASE_DIR / "structures"

def find_alanine_substrate(pdb_file):
    """Find alanine or alanine-like ligand in structure"""
    print("[1/4] Searching for alanine substrate...")
    
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("alars", pdb_file)
    
    # Look for alanine-containing residues or ligands
    scaffold_coords = {}
    target_atoms = ["N", "CA", "C", "O", "CB"]
    
    for model in structure:
        for chain in model:
            for res in chain:
                # Check for alanine or alanine-like residues
                if res.resname in ["ALA", "5A", "AMO", "AIB"]:
                    atoms_found = [atom.name for atom in res]
                    if all(a in atoms_found for a in target_atoms):
                        for a in target_atoms:
                            scaffold_coords[a] = res[a].get_coord()
                        print(f"  ✓ Found substrate: {res.resname} in chain {chain.id}")
                        return scaffold_coords, chain.id
    
    # If no ligand found, use a typical alanine residue as template
    print("  ⚠ No substrate ligand found, using residue ALA as template")
    for model in structure:
        for chain in model:
            for res in chain:
                if res.resname == "ALA" and res.id[0] == " ":
                    atoms_found = [atom.name for atom in res]
                    if all(a in atoms_found for a in target_atoms):
                        for a in target_atoms:
                            scaffold_coords[a] = res[a].get_coord()
                        print(f"  ✓ Using ALA residue {res.id[1]} as template")
                        return scaffold_coords, "X"
    
    raise ValueError("No suitable alanine template found in structure")

def build_aib_molecule(scaffold_coords):
    """Build Aib molecule and align to scaffold"""
    print("[2/4] Building Aib molecule...")
    
    # Create Aib: CC(C)(N)C(=O)O
    aib = Chem.AddHs(Chem.MolFromSmiles("CC(C)(N)C(=O)O"))
    AllChem.EmbedMolecule(aib)
    conf = aib.GetConformer()
    
    # Map atoms to scaffold
    matches = {
        "N": aib.GetSubstructMatch(Chem.MolFromSmarts("[N]"))[0],
        "C": aib.GetSubstructMatch(Chem.MolFromSmarts("[CX3](=[O])"))[0],
        "O": aib.GetSubstructMatch(Chem.MolFromSmarts("[OX1]=[C]"))[0],
        "CA": aib.GetSubstructMatch(Chem.MolFromSmarts("[CX4]([C])([C])([N])[C]"))[0]
    }
    
    # Find the two methyl groups
    ca_idx = matches["CA"]
    methyls = [m[0] for m in aib.GetSubstructMatches(Chem.MolFromSmarts("[CH3]"))]
    connected = [m for m in methyls if aib.GetBondBetweenAtoms(m, ca_idx)]
    
    if len(connected) < 2:
        raise ValueError("Could not find both methyl groups in Aib")
    
    matches["CB"] = connected[0]
    new_methyl_idx = connected[1]
    
    # Align to scaffold
    for name, idx in matches.items():
        p = scaffold_coords[name]
        conf.SetAtomPosition(idx, Point3D(float(p[0]), float(p[1]), float(p[2])))
    
    # Calculate position for second methyl (tetrahedral geometry)
    v_n = scaffold_coords["N"] - scaffold_coords["CA"]
    v_c = scaffold_coords["C"] - scaffold_coords["CA"]
    v_cb = scaffold_coords["CB"] - scaffold_coords["CA"]
    v_new = -(v_n + v_c + v_cb)
    v_new = v_new / np.linalg.norm(v_new) * 1.54  # C-C bond length
    pos_new = scaffold_coords["CA"] + v_new
    conf.SetAtomPosition(new_methyl_idx, Point3D(float(pos_new[0]), float(pos_new[1]), float(pos_new[2])))
    
    # Constrained minimization
    ff = AllChem.UFFGetMoleculeForceField(aib)
    for idx in matches.values():
        ff.AddFixedPoint(idx)
    ff.Minimize()
    
    print(f"  ✓ Aib molecule built with {aib.GetNumAtoms()} atoms")
    return aib, conf

def create_complex(pdb_file, aib, conf, ligand_chain="X"):
    """Create protein-Aib complex"""
    print("[3/4] Creating protein-Aib complex...")
    
    # Load protein
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("alars", pdb_file)
    
    # Save protein only
    class ProteinSelect(Select):
        def accept_residue(self, residue):
            return residue.id[0] == " "
    
    protein_file = STRUCTURES_DIR / "protein_temp.pdb"
    io = PDBIO()
    io.set_structure(structure)
    io.save(str(protein_file), select=ProteinSelect())
    
    # Create HETATM lines for Aib
    hetatm_lines = []
    for i, atom in enumerate(aib.GetAtoms()):
        p = conf.GetAtomPosition(i)
        element = atom.GetSymbol()
        hetatm_lines.append(
            f"HETATM{i+1:5d} {element:^4} AIB {ligand_chain}{1:4d}    "
            f"{p.x:8.3f}{p.y:8.3f}{p.z:8.3f}  1.00 20.00           {element}\n"
        )
    
    # Combine
    complex_file = STRUCTURES_DIR / "AlaRS_Aib_Complex.pdb"
    with open(complex_file, 'w') as f_out:
        with open(protein_file, 'r') as f_in:
            for line in f_in:
                if not line.startswith("END"):
                    f_out.write(line)
        f_out.write("TER\n")
        f_out.writelines(hetatm_lines)
        f_out.write("END\n")
    
    # Cleanup
    protein_file.unlink()
    
    print(f"  ✓ Complex saved: {complex_file}")
    return complex_file

def validate_complex(complex_file):
    """Validate the created complex"""
    print("[4/4] Validating complex...")
    
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("complex", complex_file)
    
    protein_atoms = 0
    ligand_atoms = 0
    
    for atom in structure.get_atoms():
        if atom.get_parent().id[0] == " ":
            protein_atoms += 1
        else:
            ligand_atoms += 1
    
    print(f"  ✓ Protein atoms: {protein_atoms}")
    print(f"  ✓ Ligand atoms: {ligand_atoms}")
    
    if ligand_atoms == 0:
        raise ValueError("No ligand atoms found in complex!")
    
    return True

def main():
    print("\n" + "="*70)
    print("  Stage 2: Aib Grafting")
    print("="*70 + "\n")
    
    input_pdb = STRUCTURES_DIR / "2ZZG_clean.pdb"
    
    # Find substrate
    scaffold_coords, chain_id = find_alanine_substrate(input_pdb)
    
    # Build Aib
    aib, conf = build_aib_molecule(scaffold_coords)
    
    # Create complex
    complex_file = create_complex(input_pdb, aib, conf, chain_id)
    
    # Validate
    validate_complex(complex_file)
    
    print("\n" + "-"*70)
    print("✓ Stage 2 Complete")
    print("-"*70)
    print(f"Output: {complex_file}")
    
    return complex_file

if __name__ == "__main__":
    main()
