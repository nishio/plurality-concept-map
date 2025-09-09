#!/usr/bin/env python3
"""
Process all markdown files in the input directory individually
Creates separate concept maps for each section
"""

import os
import subprocess
import shutil
from pathlib import Path


def get_section_id(filename):
    """Extract section ID from filename for naming output files"""
    # Remove .md extension and clean up filename
    name = filename.replace(".md", "")
    # Replace problematic characters for filesystem
    name = name.replace("⿻", "").replace("：", "-").replace("　", "")
    return name


def process_single_file(input_file, output_dir, section_id):
    """Process a single markdown file"""
    print(f"Processing {input_file} -> {section_id}")

    # Create temporary directory with just this file
    temp_input_dir = f"temp_input_{section_id}"
    os.makedirs(temp_input_dir, exist_ok=True)

    try:
        # Copy the single file to temp directory
        shutil.copy(input_file, temp_input_dir)

        # Run pipeline on this single file
        cmd = [
            "python",
            "pipeline.py",
            "--input",
            temp_input_dir,
            "--out",
            output_dir,
            "--max-concepts",
            "10",
            "--model",
            "gpt-5-mini",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✓ Successfully processed {section_id}")

            # Rename the output graph.json to include section identifier
            graph_file = os.path.join(output_dir, "graph.json")
            if os.path.exists(graph_file):
                section_graph_file = os.path.join(
                    output_dir, f"graph_{section_id}.json"
                )
                shutil.copy(graph_file, section_graph_file)
                print(f"  Created {section_graph_file}")

        else:
            print(f"✗ Failed to process {section_id}")
            print(f"Error: {result.stderr}")

    finally:
        # Clean up temp directory
        if os.path.exists(temp_input_dir):
            shutil.rmtree(temp_input_dir)


def main():
    input_dir = "input"
    base_output_dir = "output_all_sections"

    if not os.path.exists(input_dir):
        print(f"Input directory {input_dir} not found!")
        return

    # Create base output directory
    os.makedirs(base_output_dir, exist_ok=True)

    # Find all markdown files
    md_files = []
    for file in os.listdir(input_dir):
        if file.endswith(".md"):
            md_files.append(file)

    print(f"Found {len(md_files)} markdown files to process:")
    for file in md_files:
        section_id = get_section_id(file)
        print(f"  {file} -> {section_id}")

    print("\nStarting processing...")

    # Process each file
    for file in md_files:
        input_file = os.path.join(input_dir, file)
        section_id = get_section_id(file)

        process_single_file(input_file, base_output_dir, section_id)

    print(f"\n✓ Processing complete! All graphs saved in {base_output_dir}/")

    # List the generated graph files
    graph_files = [
        f
        for f in os.listdir(base_output_dir)
        if f.startswith("graph_") and f.endswith(".json")
    ]
    print(f"Generated {len(graph_files)} graph files:")
    for graph_file in sorted(graph_files):
        print(f"  {graph_file}")


if __name__ == "__main__":
    main()
