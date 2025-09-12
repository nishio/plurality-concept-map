#!/usr/bin/env python3
"""
Process individual markdown files as separate concept maps.
Each file becomes its own section with its own graph.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional
import hashlib
from datetime import datetime


def get_processed_files_record(record_file: Path) -> Dict[str, str]:
    """Read the record of previously processed files."""
    if not record_file.exists():
        return {}
    
    with open(record_file, 'r') as f:
        return json.load(f)


def save_processed_files_record(record_file: Path, record: Dict[str, str]):
    """Save the record of processed files."""
    with open(record_file, 'w') as f:
        json.dump(record, f, indent=2)


def get_file_hash(file_path: Path) -> str:
    """Get hash of file content for change detection."""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def process_single_file(
    input_file: Path,
    output_dir: Path,
    section_id: str,
    model: str = "gpt-4o-mini",
    max_concepts: int = 15,
    verbose: bool = False
) -> bool:
    """
    Process a single markdown file through the pipeline.
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Create temporary directory for single file
    temp_dir = Path(f".temp_process_{section_id}")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Copy file to temp directory
        temp_file = temp_dir / input_file.name
        temp_file.write_text(input_file.read_text(encoding='utf-8'))
        
        # Run pipeline
        cmd = [
            "python", "pipeline.py",
            "--input", str(temp_dir),
            "--out", str(output_dir),
            "--model", model,
            "--max-concepts", str(max_concepts)
        ]
        
        if verbose:
            print(f"Processing {input_file.name} -> {output_dir}")
            print(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout per file
        )
        
        if result.returncode != 0:
            print(f"Error processing {input_file.name}:")
            print(result.stderr)
            return False
            
        if verbose:
            print(f"Successfully processed {input_file.name}")
            
        return True
        
    except subprocess.TimeoutExpired:
        print(f"Timeout processing {input_file.name}")
        return False
    except Exception as e:
        print(f"Error processing {input_file.name}: {e}")
        return False
    finally:
        # Clean up temp directory
        if temp_dir.exists():
            for f in temp_dir.glob("*"):
                f.unlink()
            temp_dir.rmdir()


def process_file_list(
    file_list: List[Path],
    base_output_dir: Path,
    webui_public_dir: Path,
    prefix: str = "extra",
    model: str = "gpt-4o-mini",
    max_concepts: int = 15,
    force: bool = False,
    verbose: bool = False
) -> Dict[str, Dict]:
    """
    Process a list of markdown files individually.
    
    Args:
        file_list: List of Path objects to markdown files
        base_output_dir: Base directory for output
        webui_public_dir: WebUI public directory for graph files
        prefix: Prefix for section IDs (e.g., "extra", "custom")
        model: LLM model to use
        max_concepts: Maximum concepts per section
        force: Force reprocessing even if file hasn't changed
        verbose: Verbose output
    
    Returns:
        Dictionary mapping section IDs to processing results
    """
    results = {}
    record_file = base_output_dir / f".{prefix}_processed.json"
    processed_record = {} if force else get_processed_files_record(record_file)
    
    for idx, file_path in enumerate(file_list, start=1):
        if not file_path.exists():
            print(f"Warning: File not found: {file_path}")
            continue
            
        section_id = f"{prefix}-{idx}"
        output_dir = base_output_dir / f"output-{section_id}"
        
        # Check if file has changed
        current_hash = get_file_hash(file_path)
        file_key = str(file_path)
        
        if not force and file_key in processed_record:
            if processed_record[file_key]['hash'] == current_hash:
                if verbose:
                    print(f"Skipping unchanged file: {file_path.name}")
                results[section_id] = {
                    'status': 'skipped',
                    'file': str(file_path),
                    'reason': 'unchanged'
                }
                continue
        
        # Process the file
        print(f"\nProcessing [{idx}/{len(file_list)}]: {file_path.name}")
        success = process_single_file(
            file_path, 
            output_dir, 
            section_id,
            model=model,
            max_concepts=max_concepts,
            verbose=verbose
        )
        
        if success:
            # Copy to WebUI
            graph_file = output_dir / "graph.json"
            if graph_file.exists():
                webui_file = webui_public_dir / f"graph_{section_id}.json"
                webui_file.write_text(graph_file.read_text(encoding='utf-8'))
                
                # Update processed record
                processed_record[file_key] = {
                    'hash': current_hash,
                    'section_id': section_id,
                    'processed_at': datetime.now().isoformat(),
                    'output_dir': str(output_dir)
                }
                
                results[section_id] = {
                    'status': 'success',
                    'file': str(file_path),
                    'output': str(output_dir),
                    'webui_file': str(webui_file)
                }
                
                if verbose:
                    print(f"Copied to WebUI: {webui_file}")
            else:
                results[section_id] = {
                    'status': 'error',
                    'file': str(file_path),
                    'error': 'No graph.json generated'
                }
        else:
            results[section_id] = {
                'status': 'error',
                'file': str(file_path),
                'error': 'Processing failed'
            }
    
    # Save updated record
    save_processed_files_record(record_file, processed_record)
    
    return results


def generate_toolbar_entries(
    file_list: List[Path],
    prefix: str = "extra",
    get_title_from_file: bool = True
) -> List[Dict[str, str]]:
    """
    Generate toolbar entries for processed files.
    
    Returns:
        List of dictionaries with 'value' and 'label' keys
    """
    entries = []
    
    for idx, file_path in enumerate(file_list, start=1):
        section_id = f"{prefix}-{idx}"
        
        if get_title_from_file:
            # Try to extract title from first lines of file
            try:
                lines = file_path.read_text(encoding='utf-8').split('\n')[:10]
                # Look for a title-like line
                title = None
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('http') and len(line) > 10:
                        if '「' in line and '」' in line:
                            # Extract text between Japanese quotes
                            start = line.index('「')
                            end = line.index('」', start)
                            title = line[start+1:end]
                            break
                        elif line.startswith('#'):
                            title = line.lstrip('#').strip()
                            break
                
                if not title:
                    title = file_path.stem
                    
                label = f"{prefix.capitalize()}-{idx}: {title[:50]}"
            except:
                label = f"{prefix.capitalize()}-{idx}: {file_path.stem}"
        else:
            label = f"{prefix.capitalize()}-{idx}: {file_path.stem}"
        
        entries.append({
            'value': section_id,
            'label': label
        })
    
    return entries


def main():
    parser = argparse.ArgumentParser(
        description="Process individual markdown files as separate concept maps"
    )
    parser.add_argument(
        "--input", 
        type=str, 
        required=True,
        help="Input directory containing markdown files"
    )
    parser.add_argument(
        "--output-base",
        type=str,
        default="./individual-outputs",
        help="Base directory for outputs (default: ./individual-outputs)"
    )
    parser.add_argument(
        "--webui-public",
        type=str,
        default="./webui/public",
        help="WebUI public directory (default: ./webui/public)"
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="extra",
        help="Prefix for section IDs (default: extra)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="LLM model to use (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--max-concepts",
        type=int,
        default=15,
        help="Maximum concepts per section (default: 15)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reprocessing even if files haven't changed"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--generate-toolbar",
        action="store_true",
        help="Generate toolbar entries JSON"
    )
    
    args = parser.parse_args()
    
    # Get all markdown files from input directory
    input_dir = Path(args.input)
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)
    
    file_list = sorted(input_dir.glob("*.md"))
    if not file_list:
        print(f"No markdown files found in {input_dir}")
        sys.exit(1)
    
    print(f"Found {len(file_list)} markdown files to process")
    
    # Create output directories
    base_output_dir = Path(args.output_base)
    base_output_dir.mkdir(exist_ok=True)
    
    webui_public_dir = Path(args.webui_public)
    if not webui_public_dir.exists():
        print(f"Warning: WebUI public directory not found: {webui_public_dir}")
        webui_public_dir.mkdir(parents=True, exist_ok=True)
    
    # Process files
    results = process_file_list(
        file_list,
        base_output_dir,
        webui_public_dir,
        prefix=args.prefix,
        model=args.model,
        max_concepts=args.max_concepts,
        force=args.force,
        verbose=args.verbose
    )
    
    # Print summary
    print("\n" + "="*50)
    print("Processing Summary:")
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    skip_count = sum(1 for r in results.values() if r['status'] == 'skipped')
    error_count = sum(1 for r in results.values() if r['status'] == 'error')
    
    print(f"✓ Success: {success_count}")
    print(f"⊖ Skipped: {skip_count}")
    print(f"✗ Errors: {error_count}")
    
    if error_count > 0:
        print("\nFailed files:")
        for section_id, result in results.items():
            if result['status'] == 'error':
                print(f"  - {result['file']}: {result.get('error', 'Unknown error')}")
    
    # Generate toolbar entries if requested
    if args.generate_toolbar:
        entries = generate_toolbar_entries(file_list, prefix=args.prefix)
        toolbar_file = base_output_dir / f"{args.prefix}_toolbar_entries.json"
        with open(toolbar_file, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        print(f"\nToolbar entries saved to: {toolbar_file}")
        print("Add these to webui/src/components/Toolbar.tsx")
    
    print("\nProcessing complete!")
    
    # Return appropriate exit code
    sys.exit(0 if error_count == 0 else 1)


if __name__ == "__main__":
    main()