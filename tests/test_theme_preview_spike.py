import os
import unittest
from ui.foundation import CSS_PATH

def test_css_token_consumption_rules():
    """Verify ui/style.css exists."""
    assert os.path.exists(CSS_PATH), "ui/style.css must exist"
