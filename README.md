# ICSR Maker - E2B R3 ICSR XML Generator

A Python tool for generating E2B R3 ICSR (Individual Case Safety Report) XML files in HL7 format from JSON input data.

## Overview

This project generates standardized E2B R3 ICSR XML documents compliant with ICH (International Conference on Harmonisation) guidelines and HL7 v3 messaging standards. It's designed for pharmacovigilance use cases where adverse event reports need to be converted from JSON format to regulatory-compliant XML.

## Features

- ✅ **E2B R3 Compliant**: Generates XML following E2B R3 specifications
- ✅ **HL7 Format**: Outputs in HL7 v3 message format
- ✅ **Flexible Mapping**: CSV-based mapping between JSON and E2B tags
- ✅ **Repetitive Elements**: Handles arrays and multiple occurrences
- ✅ **Comprehensive Coverage**: Supports patient data, adverse events, drugs, diagnostic tests, and medical history
- ✅ **CLI Tool**: Easy-to-use command-line interface
- ✅ **Python Library**: Can be imported and used programmatically

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/icsrmaker.git
cd icsrmaker

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Using pip

```bash
pip install icsrmaker
```

## Quick Start

### Command Line Usage

```bash
# Basic usage
icsrmaker -i examples/sample_input.json -o output/icsr_output.xml

# With verbose output
icsrmaker -i input.json -o output.xml -v

# With custom mapping file
icsrmaker -i input.json -o output.xml -m custom_mapping.csv

# Without pretty printing
icsrmaker -i input.json -o output.xml --no-pretty
```

### Python Library Usage

```python
from icsrmaker import MappingParser, DataExtractor, ICSRXMLGenerator

# Load mapping
mapper = MappingParser('path/to/map_metadata.csv')

# Load JSON data
extractor = DataExtractor.from_file('path/to/input.json')

# Generate XML
generator = ICSRXMLGenerator(mapper)
xml_root = generator.generate(extractor)

# Save to file
generator.save_to_file(xml_root, 'output.xml')

# Or get as string
xml_string = generator.to_string(xml_root)
print(xml_string)
```

## Project Structure

```
icsrmaker/
├── src/
│   └── icsrmaker/
│       ├── __init__.py          # Package initialization
│       ├── cli.py               # Command-line interface
│       ├── mapping_parser.py    # CSV mapping parser
│       ├── data_extractor.py    # JSON data extractor
│       ├── xml_generator.py     # E2B R3 XML generator
│       └── map_metadata.csv     # E2B to JSON mapping
├── schemas/                     # XSD schema files
│   └── 4_ICH_ICSR_Schema_Files/
│       ├── coreschemas/         # Core HL7 schemas
│       └── multicacheschemas/   # E2B specific schemas
├── examples/
│   └── sample_input.json        # Example input JSON
├── output/                      # Generated XML files
├── tests/                       # Unit tests
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
└── README.md                    # This file
```

## Input JSON Format

The input JSON should follow this structure:

```json
{
  "case_id": "unique-case-id",
  "input_json": {
    "data": {
      "pv_case": {
        "identifier": "CAS-123456",
        "narrative": "Case narrative...",
        "patient": {
          "gender": "Male",
          "age": "60",
          "weight": "70",
          "height": "175"
        },
        "events": [
          {
            "name": "Adverse Event Name",
            "meddra_code": "10012345",
            "seriousness_type": "Serious",
            "outcome": {
              "name": "recovered"
            }
          }
        ],
        "drugs": [
          {
            "name": "Drug Name",
            "dosage": "100",
            "role": "Suspect Drug"
          }
        ],
        "diagnostic_tests": [...],
        "conditions": [...],
        "literature": {
          "author": {
            "name": "Author Name"
          }
        }
      }
    }
  }
}
```

See `examples/sample_input.json` for a complete example.

## Mapping CSV Format

The `map_metadata.csv` file maps E2B tags to JSON paths:

```csv
E2B Tag→JSON Path
H.1→cases[0].narrative
D.5→patient.gender
D.2.2a→patient.age
E.i.2.1b→events[_ID_].meddra_code
G.k.2.2→drugs[_ID_].name
```

### Special Notations

- **`__prefix__`**: Internal tags not present in actual XML
- **`[_ID_]`**: Indicates repetitive/array elements
- **`TBD`**: To Be Determined - not yet mapped

## E2B R3 Coverage

The generator supports the following E2B R3 sections:

### Patient Information (Section D)
- D.2.2a - Patient Age
- D.2.3 - Age Classification
- D.3 - Patient Weight
- D.4 - Patient Height
- D.5 - Patient Gender
- D.7.1.r - Medical History
- D.8.r - Past Drug History

### Adverse Events (Section E)
- E.i.2.1b - MedDRA Code
- E.i.3.1 - Seriousness Criteria
- E.i.3.2 - Outcome
- E.i.4 - Start Date
- E.i.5 - End Date
- E.i.7 - Outcome Description

### Drug Information (Section G)
- G.k.1 - Drug Role
- G.k.2.2 - Drug Name
- G.k.4.r - Dosage Information
- G.k.7.r - Indication
- G.k.8 - Action Taken
- G.k.9.i - De-challenge/Re-challenge

### Diagnostic Tests (Section F)
- F.r.1 - Test Date
- F.r.2.2b - Test Code
- F.r.3.2 - Test Result
- F.r.3.3 - Test Units

### Narrative (Section H)
- H.1 - Case Narrative

### Literature Reference (Section C)
- C.2.r - Author Information

## Output XML Structure

The generated XML follows the HL7 v3 structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MCCI_IN200100UV01 xmlns="urn:hl7-org:v3" ITSVersion="XML_1.0">
  <id extension="message-id" root="2.16.840.1.113883.3.989.2.1.3.1"/>
  <creationTime value="20231115120000"/>
  <sender>...</sender>
  <receiver>...</receiver>
  <controlActProcess>
    <subject>
      <investigationEvent>
        <!-- Patient data -->
        <!-- Adverse events -->
        <!-- Drugs -->
        <!-- Tests -->
        <!-- Medical history -->
      </investigationEvent>
    </subject>
  </controlActProcess>
</MCCI_IN200100UV01>
```

## CLI Options

```
usage: icsrmaker [-h] -i INPUT -o OUTPUT [-m MAPPING] [--message-id MESSAGE_ID]
                 [--no-pretty] [--validate] [-v]

Generate E2B R3 ICSR XML in HL7 format from JSON input

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Path to input JSON file
  -o OUTPUT, --output OUTPUT
                        Path to output XML file
  -m MAPPING, --mapping MAPPING
                        Path to CSV mapping file (default: uses bundled map_metadata.csv)
  --message-id MESSAGE_ID
                        Custom message ID (default: auto-generated UUID)
  --no-pretty           Disable pretty printing of XML
  --validate            Validate against XSD schema (requires schema files)
  -v, --verbose         Enable verbose output
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=icsrmaker tests/
```

### Code Formatting

```bash
# Format code
black src/

# Check linting
flake8 src/
```

## XSD Schema Files

The project includes E2B R3 schema files in the `schemas/` directory:

- **coreschemas/**: HL7 core data types and infrastructure
- **multicacheschemas/**: E2B-specific schemas

These schemas are from ICH and follow the official E2B R3 specification.

## Dependencies

- **lxml**: XML processing and generation
- **Python 3.7+**: Required Python version

## Use Cases

This tool is suitable for:

- Pharmacovigilance departments converting case data to E2B format
- Regulatory reporting automation
- Clinical trial safety reporting
- Healthcare IT systems integration
- Literature case extraction and reporting

## Limitations

- Schema validation is not yet implemented
- Some E2B fields may require manual mapping
- TBD (To Be Determined) fields in CSV are not included

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## References

- [ICH E2B(R3) Guidelines](https://www.ich.org/page/efficacy-guidelines)
- [HL7 v3 Messaging](https://www.hl7.org/implement/standards/product_brief.cfm?product_id=186)
- [E2B R3 Implementation Guide](https://www.ema.europa.eu/en/human-regulatory/research-development/pharmacovigilance/eudravigilance)

## Support

For issues, questions, or contributions:

- Open an issue on GitHub
- Contact: contact@example.com

## Acknowledgments

- ICH for E2B R3 specifications
- HL7 International for messaging standards
- The pharmacovigilance community

---

**Note**: This tool generates XML for informational and development purposes. Always validate generated reports against regulatory requirements before submission to health authorities.