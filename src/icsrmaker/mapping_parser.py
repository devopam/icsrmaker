"""
Mapping Parser Module
Parses the CSV mapping file that maps E2B tags to JSON paths.
"""

import csv
import re
from typing import Dict, List, Tuple
from pathlib import Path


class MappingParser:
    """
    Parses the E2B tag to JSON element mapping from CSV file.

    Handles:
    - __<> prefixed tags (internal processing, not in XML)
    - [_ID_] suffixed JSON paths (repetitive elements)
    """

    def __init__(self, csv_path: str):
        """
        Initialize the mapping parser.

        Args:
            csv_path: Path to the CSV mapping file
        """
        self.csv_path = Path(csv_path)
        self.mappings: Dict[str, str] = {}
        self.repetitive_mappings: Dict[str, str] = {}
        self.internal_mappings: Dict[str, str] = {}
        self._parse_csv()

    def _parse_csv(self):
        """Parse the CSV file and categorize mappings."""
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=',')

            for row in reader:
                if len(row) < 2:
                    continue

                # Clean the data
                e2b_tag = row[0].strip()
                json_path = row[1].strip() if len(row) > 1 else ""

                # Skip empty or TBD mappings
                if not json_path or json_path.startswith('TBD'):
                    continue

                # Check if this is an internal tag (starts with __)
                is_internal = e2b_tag.startswith('__')

                # Check if this is a repetitive element (contains [_ID_])
                is_repetitive = '[_ID_]' in json_path

                if is_internal:
                    self.internal_mappings[e2b_tag] = json_path
                elif is_repetitive:
                    # Store without the [_ID_] marker for easier processing
                    clean_path = json_path.replace('[_ID_]', '')
                    self.repetitive_mappings[e2b_tag] = clean_path
                else:
                    self.mappings[e2b_tag] = json_path

    def get_json_path(self, e2b_tag: str) -> Tuple[str, bool]:
        """
        Get the JSON path for a given E2B tag.

        Args:
            e2b_tag: The E2B tag/element name

        Returns:
            Tuple of (json_path, is_repetitive)
        """
        if e2b_tag in self.mappings:
            return self.mappings[e2b_tag], False
        elif e2b_tag in self.repetitive_mappings:
            return self.repetitive_mappings[e2b_tag], True
        elif e2b_tag in self.internal_mappings:
            return self.internal_mappings[e2b_tag], False
        else:
            return "", False

    def get_all_mappings(self) -> Dict[str, str]:
        """Get all mappings (excluding internal ones)."""
        return {**self.mappings, **self.repetitive_mappings}

    def get_repetitive_tags(self) -> List[str]:
        """Get all E2B tags that map to repetitive JSON elements."""
        return list(self.repetitive_mappings.keys())

    def is_internal_tag(self, e2b_tag: str) -> bool:
        """Check if a tag is internal (not in actual XML)."""
        return e2b_tag in self.internal_mappings

    def __repr__(self):
        return (f"MappingParser(total_mappings={len(self.mappings)}, "
                f"repetitive={len(self.repetitive_mappings)}, "
                f"internal={len(self.internal_mappings)})")
