# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-15

### Added
- Initial release of ICSR Maker
- E2B R3 ICSR XML generation in HL7 format
- CSV-based mapping system for JSON to E2B tag conversion
- Support for repetitive elements (arrays) with [_ID_] notation
- Support for internal tags with __prefix__ notation
- Command-line interface for XML generation
- Python library API for programmatic usage
- Comprehensive data extraction from nested JSON
- Patient demographics (age, gender, weight, height)
- Adverse event reporting with MedDRA codes
- Drug information with dosage, route, and action taken
- Diagnostic test results
- Medical history and conditions
- Literature reference and author information
- Outcome information (recovered, fatal, etc.)
- Seriousness criteria handling
- Pretty-print XML formatting
- Verbose logging mode
- Auto-generated message IDs
- Example usage scripts
- Complete documentation

### Supported E2B Sections
- Section C: Literature Reference
- Section D: Patient Information
- Section E: Adverse Events
- Section F: Diagnostic Tests
- Section G: Drug Information
- Section H: Case Narrative

### Technical Features
- Built on lxml for efficient XML processing
- Type hints for better code quality
- Modular architecture (mapper, extractor, generator)
- Extensible design for custom mappings
- Support for HL7 v3 messaging standard
- ICH E2B(R3) compliant structure

### Documentation
- Comprehensive README with examples
- Contributing guidelines
- Setup and installation instructions
- API usage documentation
- CLI reference
- Project structure documentation

## [Unreleased]

### Planned Features
- XSD schema validation
- Support for E2B R2 format
- Additional output formats (JSON, database)
- Batch processing capabilities
- Web interface
- Enhanced error handling and validation
- Performance optimizations
- Extended field coverage
- Integration with pharmacovigilance systems
