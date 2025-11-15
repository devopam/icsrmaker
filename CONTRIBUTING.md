# Contributing to ICSR Maker

Thank you for your interest in contributing to ICSR Maker! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/icsrmaker.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Install development dependencies: `pip install -e ".[dev]"`

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/icsrmaker.git
cd icsrmaker

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

## Project Structure

```
icsrmaker/
├── src/icsrmaker/      # Main source code
├── tests/              # Unit tests
├── examples/           # Example files
├── schemas/            # XSD schemas
└── docs/               # Documentation
```

## Code Style

We use the following tools for code quality:

- **black**: Code formatting (line length: 100)
- **flake8**: Linting
- **mypy**: Type checking (optional)

Run formatters before committing:

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

## Testing

All new features should include tests. We use pytest for testing.

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=icsrmaker tests/

# Run specific test file
pytest tests/test_mapping_parser.py

# Run with verbose output
pytest -v tests/
```

### Writing Tests

Place test files in the `tests/` directory following the pattern `test_*.py`:

```python
import pytest
from icsrmaker import MappingParser

def test_mapping_parser_loads_csv():
    """Test that mapping parser correctly loads CSV."""
    parser = MappingParser('path/to/test.csv')
    assert len(parser.mappings) > 0
```

## Making Changes

1. **Create a branch**: Use descriptive names like `feature/add-validation` or `fix/csv-parsing`

2. **Make your changes**: Follow the existing code style and patterns

3. **Add tests**: Ensure your changes are covered by tests

4. **Update documentation**: Update README.md or add docstrings as needed

5. **Run tests**: Make sure all tests pass

6. **Commit**: Use clear, descriptive commit messages

```bash
git add .
git commit -m "Add validation for XSD schemas"
```

## Commit Message Guidelines

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests when relevant

Examples:
```
Add support for E2B R2 format
Fix CSV parsing for Windows line endings
Update documentation for CLI usage
```

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the version number in `setup.py` if appropriate
3. Ensure all tests pass
4. Request review from maintainers

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style
- [ ] Documentation updated
- [ ] No new warnings
```

## Areas for Contribution

We welcome contributions in the following areas:

### High Priority
- XSD validation implementation
- Support for more E2B fields
- Unit test coverage
- Performance optimization
- Error handling improvements

### Medium Priority
- Support for E2B R2 format
- Additional output formats (JSON, database)
- Documentation improvements
- Example use cases

### Nice to Have
- Web interface
- Batch processing
- Integration with pharmacovigilance systems
- Support for other regulatory formats (MedWatch, PSUR)

## Coding Standards

### Python Style
- Follow PEP 8
- Use type hints where possible
- Write descriptive docstrings
- Keep functions focused and small

### Documentation
- All public functions must have docstrings
- Use Google-style docstring format
- Include examples in docstrings for complex functions

Example:
```python
def generate_xml(data: Dict[str, Any]) -> etree.Element:
    """
    Generate E2B R3 ICSR XML from input data.

    Args:
        data: Dictionary containing case data

    Returns:
        XML element representing the ICSR document

    Raises:
        ValueError: If required fields are missing

    Examples:
        >>> data = {"patient": {"age": 60}}
        >>> xml = generate_xml(data)
    """
    pass
```

## Reporting Issues

When reporting issues, please include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Detailed steps to reproduce the problem
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: Python version, OS, package versions
6. **Sample Data**: If possible, include sample input (anonymized)

## Questions?

- Open an issue for questions
- Check existing issues first
- Be respectful and constructive

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions help make ICSR Maker better for everyone in the pharmacovigilance community!
