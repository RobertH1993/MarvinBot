import unittest
import secrets
from config import Config


class TestConfig(unittest.TestCase):
    def test_open_save_and_read_config(self):
        test_config = Config("test/data/config.json")
        test_token = secrets.token_hex(16)
        test_config['write_test_key'] = test_token
        test_config.save()
        
        # Reload config to pull data from disk, we want to test if it gets actually saved to disk
        test_config.reload()
        self.assertEqual(test_config['write_test_key'], test_token)
