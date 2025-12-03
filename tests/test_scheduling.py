import unittest
import json
from datetime import datetime
from video_publisher.metadata import validate_metadata, generate_template, merge_metadata

class TestScheduling(unittest.TestCase):
    def test_template_generation(self):
        """Test that template includes scheduling object."""
        template = generate_template()
        self.assertIn('scheduling', template)
        self.assertIn('publish_now', template['scheduling'])
        self.assertIn('scheduled_time', template['scheduling'])
        self.assertTrue(template['scheduling']['publish_now'])
        self.assertIsNone(template['scheduling']['scheduled_time'])

    def test_validation_valid_scheduling(self):
        """Test validation with valid scheduling data."""
        metadata = {
            "scheduling": {
                "publish_now": True,
                "scheduled_time": None
            }
        }
        is_valid, error = validate_metadata(metadata)
        self.assertTrue(is_valid, f"Validation failed: {error}")

        metadata_scheduled = {
            "scheduling": {
                "publish_now": False,
                "scheduled_time": "2025-12-25T10:00:00Z"
            }
        }
        is_valid, error = validate_metadata(metadata_scheduled)
        self.assertTrue(is_valid, f"Validation failed: {error}")

    def test_validation_invalid_scheduling(self):
        """Test validation with invalid scheduling data."""
        # Invalid type for publish_now
        metadata = {
            "scheduling": {
                "publish_now": "yes", 
                "scheduled_time": None
            }
        }
        is_valid, error = validate_metadata(metadata)
        self.assertFalse(is_valid)
        
        # Invalid type for scheduled_time (should be string or null)
        metadata = {
            "scheduling": {
                "publish_now": False,
                "scheduled_time": 12345
            }
        }
        is_valid, error = validate_metadata(metadata)
        self.assertFalse(is_valid)

    def test_merge_metadata(self):
        """Test merging CLI arguments into metadata."""
        base = {"title": "Base"}
        override = {
            "scheduling": {
                "publish_now": True,
                "scheduled_time": None
            }
        }
        merged = merge_metadata(base, override)
        self.assertTrue(merged['scheduling']['publish_now'])

if __name__ == '__main__':
    unittest.main()
