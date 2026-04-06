import unittest
import json
import os
import shutil
from pathlib import Path
from unittest.mock import patch

# We need to patch CONFIG_DIR in config.py before importing its functions
# to avoid writing to the actual user's home directory.
import config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("/tmp/test_linux_agent")
        self.test_file = self.test_dir / "config.json"
        
        # Patch config constants
        self.config_dir_patch = patch('config.CONFIG_DIR', self.test_dir)
        self.config_file_patch = patch('config.CONFIG_FILE', self.test_file)
        self.config_dir_patch.start()
        self.config_file_patch.start()
        
        # Clean up any existing test dir
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def tearDown(self):
        self.config_dir_patch.stop()
        self.config_file_patch.stop()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_ensure_config_dir(self):
        self.assertFalse(self.test_dir.exists())
        config.ensure_config_dir()
        self.assertTrue(self.test_dir.exists())

    def test_load_config_default(self):
        # Should return deep copy of default config when file doesn't exist
        cfg = config.load_config()
        self.assertEqual(cfg, config.DEFAULT_CONFIG)
        
        # Mutating shouldn't affect DEFAULT_CONFIG
        cfg["search"]["language"] = "fr"
        self.assertEqual(config.DEFAULT_CONFIG["search"]["language"], "en")

    def test_save_and_load_config(self):
        cfg = config.load_config()
        cfg["search"]["language"] = "ar"
        config.save_config(cfg)
        
        # Reload
        loaded = config.load_config()
        self.assertEqual(loaded["search"]["language"], "ar")

    def test_get_setting(self):
        self.assertEqual(config.get_setting("search.language"), "en")
        self.assertEqual(config.get_setting("auto_fix.enabled"), True)
        self.assertIsNone(config.get_setting("nonexistent.setting"))

    def test_set_setting(self):
        self.assertTrue(config.set_setting("search.language", "ar"))
        self.assertEqual(config.get_setting("search.language"), "ar")
        
        # Check it persisted
        loaded = config.load_config()
        self.assertEqual(loaded["search"]["language"], "ar")

    def test_reset_config(self):
        config.set_setting("search.language", "ar")
        self.assertEqual(config.get_setting("search.language"), "ar")
        config.reset_config()
        self.assertEqual(config.get_setting("search.language"), "en")

if __name__ == '__main__':
    unittest.main()
