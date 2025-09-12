#!/usr/bin/env python3
"""
SRIM Binary File Reader
Attempts to extract depth profile data from SRIM .sav files
"""

import numpy as np
import matplotlib.pyplot as plt
import struct
import os

def read_srim_range_file(filepath):
    """
    Read SRIM XRANGE.sav file (oxygen depth profile)
    SRIM typically stores range data as binary arrays
    """
    try:
        with open(filepath, 'rb') as f:
            # SRIM files often start with header information
            # The exact format depends on SRIM version
            
            # Skip potential header (common sizes: 100, 200, 400 bytes)
            header_sizes = [100, 200, 400, 0]
            
            for header_size in header_sizes:
                f.seek(header_size)
                
                # Try to read as array of floats (common SRIM format)
                remaining_bytes = os.path.getsize(filepath) - header_size
                num_floats = remaining_bytes // 4  # 4 bytes per float
                
                if num_floats > 0:
                    try:
                        data = struct.unpack(f'{num_floats}f', f.read(num_floats * 4))
                        
                        # SRIM range files often have depth,concentration pairs
                        if len(data) % 2 == 0:
                            pairs = len(data) // 2
                            depths = data[0::2]  # Even indices
                            concentrations = data[1::2]  # Odd indices
                            
                            # Filter out invalid data
                            valid_mask = np.array(concentrations) > 0
                            if np.any(valid_mask):
                                return np.array(depths)[valid_mask], np.array(concentrations)[valid_mask]
                        
                        # If not pairs, try as single array (depths or concentrations)
                        elif len(data) > 10:  # Reasonable data size
                            # Create synthetic depth array
                            depths = np.linspace(0, len(data)*10, len(data))
                            return depths, np.array(data)
                            
                    except struct.error:
                        continue
                        
        print(f"Could not parse {filepath} - unknown format")
        return None, None
        
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None, None

def read_srim_vacancy_file(filepath):
    """
    Read SRIM VACANCY.sav file (vacancy depth profile)
    Similar format to range file but for vacancy data
    """
    return read_srim_range_file(filepath)  # Same parsing approach

def analyze_real_srim_data():
    """Analyze actual SRIM data files"""
    
    base_path = "/home/fatduck/git/nanofabrication/tutorial/tut3/Results"
    energies = ["2keV", "8keV", "16keV", "30keV"]
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('SRIM Analysis: Real Data Extraction\nO+ Ion Implantation vs Carbon Vacancies', fontsize=14)
    
    results = {}
    
    for i, energy in enumerate(energies):
        ax = axes[i//2, i%2]
        folder_path = f"{base_path}/O{energy}"
        
        range_file = f"{folder_path}/XRANGE.sav"
        vacancy_file = f"{folder_path}/VACANCY.sav"
        
        ax.set_title(f'Oxygen {energy} Implantation')
        ax.set_xlabel('Depth (Angstroms)')
        ax.set_ylabel('Relative Concentration')
        
        # Read oxygen profile
        o_depths, o_conc = read_srim_range_file(range_file)
        
        # Read vacancy profile  
        v_depths, v_conc = read_srim_vacancy_file(vacancy_file)
        
        if o_depths is not None and len(o_depths) > 0:
            # Normalize concentrations for comparison
            o_conc_norm = np.array(o_conc) / np.max(o_conc)
            ax.plot(o_depths, o_conc_norm, 'b-', linewidth=2, label='Implanted O atoms')
            results[f"{energy}_oxygen"] = (o_depths, o_conc_norm)
            print(f"✓ Successfully read oxygen data for {energy}")
        else:
            print(f"✗ Could not read oxygen data for {energy}")
            
        if v_depths is not None and len(v_depths) > 0:
            # Normalize concentrations for comparison
            v_conc_norm = np.array(v_conc) / np.max(v_conc)
            ax.plot(v_depths, v_conc_norm, 'r--', linewidth=2, label='Carbon vacancies')
            results[f"{energy}_vacancy"] = (v_depths, v_conc_norm)
            print(f"✓ Successfully read vacancy data for {energy}")
        else:
            print(f"✗ Could not read vacancy data for {energy}")
        
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, None)
        ax.set_ylim(0, 1.1)
    
    plt.tight_layout()
    plt.savefig(f'{base_path}/real_srim_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return results

def examine_file_structure():
    """Examine the structure of SRIM files to understand format"""
    
    base_path = "/home/fatduck/git/nanofabrication/tutorial/tut3/Results"
    
    print("SRIM File Structure Analysis")
    print("=" * 50)
    
    # Check one example from each energy
    for energy in ["2keV", "16keV"]:
        folder_path = f"{base_path}/O{energy}"
        
        print(f"\n{energy} Files:")
        print("-" * 20)
        
        # Examine key files
        files_to_check = ["XRANGE.sav", "VACANCY.sav", "STOPPING.sav"]
        
        for filename in files_to_check:
            filepath = f"{folder_path}/{filename}"
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"{filename}: {size} bytes")
                
                # Read first few bytes to check format
                with open(filepath, 'rb') as f:
                    header = f.read(min(100, size))
                    print(f"  First 20 bytes (hex): {header[:20].hex()}")
                    
                    # Check if it contains text
                    try:
                        text_sample = header.decode('ascii', errors='ignore')
                        if any(c.isprintable() and c not in '\x00\x01\x02\x03' for c in text_sample[:50]):
                            print(f"  Contains text: {repr(text_sample[:50])}")
                    except:
                        pass
            else:
                print(f"{filename}: NOT FOUND")

if __name__ == "__main__":
    print("SRIM Data Extraction Tool")
    print("=" * 40)
    
    # First examine file structure
    examine_file_structure()
    
    print("\n" + "=" * 40)
    print("Attempting to extract depth profile data...")
    
    # Try to extract real data
    results = analyze_real_srim_data()
    
    if not any(results):
        print("\nCould not extract data from binary files.")
        print("The files might need specialized SRIM tools or different parsing.")
        print("Consider using SRIM's built-in export functions or SRIMlib.")
    else:
        print(f"\nSuccessfully extracted data from {len(results)} datasets")
