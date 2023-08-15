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

    def test_contains_method(self):
        test_config = Config("test/data/config.json")
        self.assertNotIn('test_contains', test_config)
        test_config['test_contains'] = True
        self.assertIn('test_contains', test_config)

    def test_del_method(self):
        test_config = Config("test/data/config.json")
        test_config['test_del'] = True
        del test_config['test_del']
        self.assertNotIn('test_del', test_config)

    def test_change_and_reload_config(self):
        test_config = Config("test/data/config.json")
        test_config['test_reload'] = secrets.token_hex(16)

        test_config.reload()
        self.assertNotIn('test_reload', test_config)

