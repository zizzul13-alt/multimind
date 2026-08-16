"""
MultiMind AI - Theme Contract Models
Defines dataclasses for themes and theme metadata.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class ThemeMetadata:
    """Minimal metadata hook for future Design DNA and asset provenance tracking."""
    description: str = ""
    author: str = ""
    license: str = ""
    source: str = ""
    attribution: str = ""
    reference: str = ""
    asset_scope: str = ""


@dataclass
class Theme:
    """Explicit Theme contract representing visual token overrides for MultiMind AI."""
    id: str
    display_name: str
    category: str = "system"
    description: str = ""
    metadata: Optional[ThemeMetadata] = None
    colors: Optional[Dict[str, str]] = field(default_factory=dict)
    typography: Optional[Dict[str, Any]] = field(default_factory=dict)
    spacing: Optional[Dict[str, str]] = field(default_factory=dict)
    radius: Optional[Dict[str, str]] = field(default_factory=dict)
    surfaces: Optional[Dict[str, str]] = field(default_factory=dict)
    borders: Optional[Dict[str, str]] = field(default_factory=dict)

    def validate(self):
        """Validates theme contract constraints."""
        if not self.id or not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Theme 'id' must be a non-empty string.")
        if not self.display_name or not isinstance(self.display_name, str) or not self.display_name.strip():
            raise ValueError("Theme 'display_name' must be a non-empty string.")
