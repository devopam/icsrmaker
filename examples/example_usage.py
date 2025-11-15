#!/usr/bin/env python3
"""
Example usage of the ICSR Maker library.
Demonstrates how to use the Python API directly.
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from icsrmaker import MappingParser, DataExtractor, ICSRXMLGenerator


def main():
    """Main example function."""
    # Paths
    base_dir = Path(__file__).parent.parent
    input_json = base_dir / 'examples' / 'sample_input.json'
    mapping_csv = base_dir / 'src' / 'icsrmaker' / 'map_metadata.csv'
    output_xml = base_dir / 'output' / 'example_output.xml'

    print("ICSR Maker - Example Usage")
    print("=" * 50)

    # Step 1: Load the mapping
    print("\n1. Loading E2B to JSON mapping...")
    mapper = MappingParser(str(mapping_csv))
    print(f"   ✓ Loaded {mapper}")

    # Step 2: Load the JSON data
    print("\n2. Loading input JSON data...")
    extractor = DataExtractor.from_file(str(input_json))
    print(f"   ✓ Loaded {extractor}")

    # Step 3: Generate the XML
    print("\n3. Generating E2B R3 ICSR XML...")
    generator = ICSRXMLGenerator(mapper)
    xml_root = generator.generate(extractor)
    print("   ✓ XML structure created")

    # Step 4: Save to file
    print("\n4. Saving to file...")
    output_xml.parent.mkdir(parents=True, exist_ok=True)
    generator.save_to_file(xml_root, str(output_xml), pretty_print=True)
    print(f"   ✓ Saved to: {output_xml}")

    # Step 5: Display some statistics
    print("\n5. XML Statistics:")
    xml_string = generator.to_string(xml_root)
    print(f"   - Size: {len(xml_string)} bytes")
    print(f"   - Lines: {xml_string.count(chr(10))} lines")

    # Extract some sample data to show what was included
    case_id = extractor.extract('pv_case.identifier')
    patient_age = extractor.extract('pv_case.patient.age')
    patient_gender = extractor.extract('pv_case.patient.gender')
    num_events = extractor.get_array_length('pv_case.events')
    num_drugs = extractor.get_array_length('pv_case.drugs')
    num_tests = extractor.get_array_length('pv_case.diagnostic_tests')

    print(f"\n6. Case Summary:")
    print(f"   - Case ID: {case_id}")
    print(f"   - Patient: {patient_age} year old {patient_gender}")
    print(f"   - Adverse Events: {num_events}")
    print(f"   - Drugs: {num_drugs}")
    print(f"   - Diagnostic Tests: {num_tests}")

    print("\n" + "=" * 50)
    print("✓ Example completed successfully!")
    print(f"Output file: {output_xml}")


if __name__ == '__main__':
    main()
