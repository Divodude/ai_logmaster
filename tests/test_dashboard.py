"""
Unit tests for Dashboard Server helpers and validation
"""
import unittest
from ai_logmaster.dashboard.server import _default_config, _test_connection


class TestDashboardServer(unittest.TestCase):

    def test_default_config_schema(self):
        config = _default_config()
        self.assertIn("ai", config)
        self.assertIn("agent", config)
        self.assertIn("documentation", config)
        self.assertIn("output", config)
        self.assertEqual(config["ai"]["provider"], "groq")

    def test_test_connection_empty_api_key(self):
        config = {
            "ai": {
                "provider": "groq",
                "model": "llama-3.3-70b-versatile",
                "api_key": "",
            }
        }
        result = _test_connection(config)
        self.assertFalse(result["success"])
        self.assertIn("empty", result["message"].lower())

    def test_test_connection_empty_model(self):
        config = {
            "ai": {
                "provider": "groq",
                "model": "",
                "api_key": "some-key",
            }
        }
        result = _test_connection(config)
        self.assertFalse(result["success"])
        self.assertIn("model", result["message"].lower())


if __name__ == "__main__":
    unittest.main()
