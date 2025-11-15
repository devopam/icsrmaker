"""
Data Extractor Module
Extracts data from JSON using the parsed mappings.
"""

import json
from typing import Any, List, Dict, Optional
from pathlib import Path
import re


class DataExtractor:
    """
    Extracts data from JSON input using E2B tag mappings.

    Handles:
    - Nested JSON paths (e.g., "patient.gender")
    - Array indexing (e.g., "events[0].name")
    - Multiple array elements (e.g., "drugs[_ID_]")
    """

    def __init__(self, json_data: Dict[str, Any]):
        """
        Initialize the data extractor.

        Args:
            json_data: The input JSON data dictionary
        """
        self.data = json_data
        # Navigate to the actual data if it's wrapped
        if 'input_json' in self.data and 'data' in self.data['input_json']:
            self.base_data = self.data['input_json']['data']
        elif 'data' in self.data:
            self.base_data = self.data['data']
        else:
            self.base_data = self.data

    @classmethod
    def from_file(cls, json_path: str) -> 'DataExtractor':
        """
        Create a DataExtractor from a JSON file.

        Args:
            json_path: Path to the JSON file

        Returns:
            DataExtractor instance
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(data)

    def extract(self, json_path: str, index: Optional[int] = None) -> Any:
        """
        Extract data from JSON using a dot-notation path.

        Args:
            json_path: Dot-notation path (e.g., "patient.gender" or "events.name")
            index: Optional index for array elements

        Returns:
            The extracted value or None if not found
        """
        if not json_path:
            return None

        # Start with base data or full data
        current = self.base_data

        # Split the path by dots
        parts = json_path.split('.')

        for part in parts:
            if current is None:
                return None

            # Handle array notation like events[0]
            array_match = re.match(r'(\w+)\[(\d+)\]', part)
            if array_match:
                key = array_match.group(1)
                idx = int(array_match.group(2))
                if isinstance(current, dict) and key in current:
                    current = current[key]
                    if isinstance(current, list) and idx < len(current):
                        current = current[idx]
                    else:
                        return None
                else:
                    return None
            else:
                # Regular key access
                if isinstance(current, dict) and part in current:
                    current = current[part]
                elif isinstance(current, list) and index is not None and index < len(current):
                    # If current is a list and we have an index, use it
                    current = current[index]
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        return None
                else:
                    return None

        return current

    def extract_multiple(self, json_path: str) -> List[Any]:
        """
        Extract multiple values from an array path.

        Args:
            json_path: Path to array elements (e.g., "events.name")

        Returns:
            List of extracted values
        """
        if not json_path:
            return []

        # Navigate to the parent array
        parts = json_path.split('.')
        if len(parts) < 2:
            return []

        # Get the array parent path and the field to extract
        array_path = '.'.join(parts[:-1])
        field = parts[-1]

        array_data = self.extract(array_path)

        if not isinstance(array_data, list):
            return []

        results = []
        for item in array_data:
            if isinstance(item, dict) and field in item:
                results.append(item[field])

        return results

    def get_array_length(self, array_path: str) -> int:
        """
        Get the length of an array at the specified path.

        Args:
            array_path: Path to the array (e.g., "events" or "drugs")

        Returns:
            Length of the array, or 0 if not found
        """
        array_data = self.extract(array_path)
        if isinstance(array_data, list):
            return len(array_data)
        return 0

    def extract_with_path(self, json_path: str, array_index: Optional[int] = None) -> Any:
        """
        Extract data handling both simple and array paths.

        Args:
            json_path: The JSON path
            array_index: Optional index for array elements

        Returns:
            Extracted value or None
        """
        # Handle paths with array markers
        if '[' in json_path and ']' in json_path:
            # This is already an indexed path
            return self.extract(json_path)
        else:
            # Check if this should be an array access
            parts = json_path.split('.')
            if len(parts) >= 2:
                # Check if the first part is an array
                potential_array = self.extract(parts[0])
                if isinstance(potential_array, list) and array_index is not None:
                    # Reconstruct the path with index
                    if array_index < len(potential_array):
                        return self.extract(json_path, index=array_index)

            return self.extract(json_path)

    def get_root_data(self) -> Dict[str, Any]:
        """Get the root data object."""
        return self.data

    def get_base_data(self) -> Dict[str, Any]:
        """Get the base data object (unwrapped)."""
        return self.base_data

    def __repr__(self):
        return f"DataExtractor(data_keys={list(self.base_data.keys())})"
