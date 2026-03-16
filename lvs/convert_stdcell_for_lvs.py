#!/usr/bin/env python3
"""
Convert GF180MCU standard cell SPICE netlist for KLayout LVS compatibility.

Conversions performed:
1. Device names from X_* to M_* for MOSFET devices (nfet/pfet lines)
2. Device models from pfet_06v0 to pfet_05v0
3. Device models from nfet_06v0 to nfet_05v0

This is needed for KLayout LVS which expects M* prefixes for MOSFET devices,
but the GF180MCU PDK uses subcircuit-style X_* instantiation.

Usage:
    python convert_stdcell_for_lvs.py [input.spice] [output.spice]
    
Defaults:
    input:  ./gf180mcu_fd_sc_mcu9t5v0.spice
    output: ./gf180mcu_fd_sc_mcu9t5v0_lvs.spice
"""

import re
import sys
import os

# Default input file (relative to script location)
DEFAULT_INPUT = "gf180mcu_fd_sc_mcu9t5v0.spice"


def convert_netlist(input_file, output_file=None):
    """
    Convert X_* device names to M_* for lines containing nfet or pfet.
    Also convert pfet_06v0 to pfet_05v0 and nfet_06v0 to nfet_05v0.
    
    Args:
        input_file: Path to input SPICE netlist
        output_file: Path to output file (optional, defaults to input_lvs.spice)
    
    Returns:
        Tuple of (lines_modified, total_lines)
    """
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_lvs{ext}"
    
    # Pattern to match lines starting with X_ that contain nfet or pfet
    # This matches X_ followed by any identifier at the start of a line
    pattern = re.compile(r'^(X_)(\S+)(.*(nfet|pfet).*)', re.IGNORECASE)
    
    lines_modified = 0
    total_lines = 0
    
    with open(input_file, 'r') as infile:
        lines = infile.readlines()
    
    total_lines = len(lines)
    output_lines = []
    
    for line in lines:
        modified = False
        new_line = line
        
        # Check if line starts with X_ and contains nfet or pfet
        match = pattern.match(line)
        if match:
            # Replace X_ with M_ at the start of the line
            new_line = 'M_' + match.group(2) + match.group(3) + '\n'
            modified = True
        
        # Convert device model names from 06v0 to 05v0
        if 'pfet_06v0' in new_line:
            new_line = new_line.replace('pfet_06v0', 'pfet_05v0')
            modified = True
        if 'nfet_06v0' in new_line:
            new_line = new_line.replace('nfet_06v0', 'nfet_05v0')
            modified = True
        
        output_lines.append(new_line)
        if modified:
            lines_modified += 1
    
    with open(output_file, 'w') as outfile:
        outfile.writelines(output_lines)
    
    return lines_modified, total_lines, output_file


def main():
    # Get script directory for default input file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_input_path = os.path.join(script_dir, DEFAULT_INPUT)
    
    # Parse arguments
    if len(sys.argv) >= 2 and sys.argv[1] in ('-h', '--help'):
        print(__doc__)
        sys.exit(0)
    
    input_file = sys.argv[1] if len(sys.argv) > 1 else default_input_path
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    print(f"Converting: {input_file}")
    lines_modified, total_lines, out_path = convert_netlist(input_file, output_file)
    
    print(f"Output:     {out_path}")
    print(f"Modified:   {lines_modified} / {total_lines} lines")
    print("Done!")


if __name__ == "__main__":
    main()

