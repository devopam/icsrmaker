"""
Command Line Interface for E2B R3 ICSR XML Generator
"""

import argparse
import sys
from pathlib import Path
import json
from typing import Optional

from .mapping_parser import MappingParser
from .data_extractor import DataExtractor
from .xml_generator import ICSRXMLGenerator


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate E2B R3 ICSR XML in HL7 format from JSON input',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate XML from JSON input
  python -m icsrmaker.cli -i input.json -o output.xml

  # Specify custom mapping CSV
  python -m icsrmaker.cli -i input.json -o output.xml -m custom_mapping.csv

  # Generate without pretty printing
  python -m icsrmaker.cli -i input.json -o output.xml --no-pretty
        """
    )

    parser.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        help='Path to input JSON file'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help='Path to output XML file'
    )

    parser.add_argument(
        '-m', '--mapping',
        type=str,
        default=None,
        help='Path to CSV mapping file (default: uses bundled map_metadata.csv)'
    )

    parser.add_argument(
        '--message-id',
        type=str,
        default=None,
        help='Custom message ID (default: auto-generated UUID)'
    )

    parser.add_argument(
        '--no-pretty',
        action='store_true',
        help='Disable pretty printing of XML'
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate against XSD schema (requires schema files)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    try:
        # Validate input file exists
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            return 1

        # Determine mapping file path
        if args.mapping:
            mapping_path = Path(args.mapping)
        else:
            # Use bundled mapping file
            mapping_path = Path(__file__).parent / 'map_metadata.csv'

        if not mapping_path.exists():
            print(f"Error: Mapping file not found: {mapping_path}", file=sys.stderr)
            return 1

        if args.verbose:
            print(f"Loading input JSON: {input_path}")
            print(f"Loading mapping CSV: {mapping_path}")

        # Load mapping
        mapper = MappingParser(str(mapping_path))
        if args.verbose:
            print(f"Loaded {mapper}")

        # Load JSON data
        extractor = DataExtractor.from_file(str(input_path))
        if args.verbose:
            print(f"Loaded {extractor}")

        # Generate XML
        if args.verbose:
            print("Generating E2B R3 ICSR XML...")

        generator = ICSRXMLGenerator(mapper)
        xml_root = generator.generate(extractor, message_id=args.message_id)

        # Save to file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        generator.save_to_file(
            xml_root,
            str(output_path),
            pretty_print=not args.no_pretty
        )

        print(f"Successfully generated E2B R3 ICSR XML: {output_path}")

        # Optional validation
        if args.validate:
            if args.verbose:
                print("Validating XML against schema...")
            # TODO: Implement XSD validation
            print("Note: Schema validation not yet implemented")

        return 0

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
