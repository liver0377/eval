#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Merge all JSON files in a directory into a single JSONL file.

JSONL format: One JSON object per line

Usage:
    python merge_json_to_jsonl.py <input_dir> <output_jsonl>

Example:
    python merge_json_to_jsonl.py data/dataset/tmp/sub_real output.jsonl
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any


def load_json_files(input_dir: str) -> List[Dict[str, Any]]:
    """
    Load all JSON files from input directory, sorted alphabetically.

    Args:
        input_dir: Path to directory containing JSON files

    Returns:
        List of JSON objects sorted by filename
    """
    input_path = Path(input_dir)

    if not input_path.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    if not input_path.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_dir}")

    # Get all JSON files, sorted alphabetically
    json_files = sorted(input_path.glob("*.json"))

    if not json_files:
        raise ValueError(f"No JSON files found in directory: {input_dir}")

    print(f"Found {len(json_files)} JSON files in {input_dir}")

    # Load all JSON files
    json_objects = []
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                json_objects.append(data)
                print(f"  Loaded: {json_file.name}")
        except json.JSONDecodeError as e:
            print(f"  [ERROR] Failed to parse {json_file.name}: {e}")
            raise
        except Exception as e:
            print(f"  [ERROR] Failed to read {json_file.name}: {e}")
            raise

    return json_objects


def write_jsonl(output_file: str, json_objects: List[Dict[str, Any]]) -> None:
    """
    Write JSON objects to a JSONL file (one JSON per line).

    Args:
        output_file: Path to output JSONL file
        json_objects: List of JSON objects to write
    """
    output_path = Path(output_file)

    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for obj in json_objects:
            # Write each JSON object as a single line
            json.dump(obj, f, ensure_ascii=False)
            f.write('\n')

    print(f"\nSuccessfully wrote {len(json_objects)} records to {output_file}")


def validate_json_objects(json_objects: List[Dict[str, Any]]) -> None:
    """
    Validate that all JSON objects have required fields.

    Args:
        json_objects: List of JSON objects to validate

    Raises:
        ValueError: If validation fails
    """
    required_fields = ['key', 'messages', 'rule_list']

    for i, obj in enumerate(json_objects, 1):
        # Check required fields
        missing_fields = [field for field in required_fields if field not in obj]
        if missing_fields:
            raise ValueError(
                f"Object {i} (key={obj.get('key', 'N/A')}) "
                f"is missing required fields: {missing_fields}"
            )

        # Validate messages is a non-empty list
        if not isinstance(obj['messages'], list) or len(obj['messages']) == 0:
            raise ValueError(
                f"Object {i} (key={obj['key']}) "
                f"has invalid or empty 'messages' field"
            )

        # Validate rule_list is a list
        if not isinstance(obj['rule_list'], list):
            raise ValueError(
                f"Object {i} (key={obj['key']}) "
                f"'rule_list' must be a list"
            )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Merge JSON files in a directory into a single JSONL file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Merge all JSON files from sub_real directory
  python merge_json_to_jsonl.py data/dataset/tmp/sub_real output.jsonl

  # Merge with custom output path
  python merge_json_to_jsonl.py ./input_dir ./output/merged.jsonl

  # Merge without validation
  python merge_json_to_jsonl.py data/dataset/tmp/sub_real output.jsonl --no-validate
        """
    )

    parser.add_argument(
        'input_dir',
        help='Input directory containing JSON files'
    )

    parser.add_argument(
        'output_file',
        help='Output JSONL file path'
    )

    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip validation of JSON objects'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    try:
        print("="*80)
        print("JSON to JSONL Merger")
        print("="*80)
        print(f"Input directory: {args.input_dir}")
        print(f"Output file: {args.output_file}")
        print("="*80)

        # Load JSON files
        json_objects = load_json_files(args.input_dir)

        # Validate JSON objects
        if not args.no_validate:
            print("\nValidating JSON objects...")
            validate_json_objects(json_objects)
            print("  All objects are valid!")

        # Write JSONL file
        print(f"\nWriting JSONL file...")
        write_jsonl(args.output_file, json_objects)

        # Show summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total objects merged: {len(json_objects)}")
        print(f"Input directory: {args.input_dir}")
        print(f"Output file: {args.output_file}")
        print(f"File size: {os.path.getsize(args.output_file)} bytes")
        print("="*80)

        if args.verbose:
            print("\nObject keys:")
            for i, obj in enumerate(json_objects, 1):
                key = obj.get('key', 'N/A')
                messages_count = len(obj.get('messages', []))
                rules_count = len(obj.get('rule_list', []))
                print(f"  {i:3d}. key={key:5s} | messages={messages_count:2d} | rules={rules_count:2d}")

    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
