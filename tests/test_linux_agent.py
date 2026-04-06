import unittest
from unittest.mock import patch, MagicMock
import shlex

import linux_agent

class TestLinuxAgent(unittest.TestCase):

    @patch('subprocess.run')
    def test_install_package_injection(self, mock_run):
        # Mock subprocess.run to avoid actual execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Installed"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        malicious_input = "htop; rm -rf /"
        
        # Expected command should have the malicious input escaped
        linux_agent.install_package.invoke({"package_name": malicious_input})
        
        called_cmd = mock_run.call_args[0][0]
        # Our malicious input should be enclosed in quotes by shlex.quote
        expected_quoted = shlex.quote(malicious_input)
        
        self.assertIn(expected_quoted, called_cmd)
        self.assertNotIn("; rm -rf / ", called_cmd) # The raw string shouldn't be executed as a separate command

    @patch('subprocess.run')
    def test_clean_system_stderr_inclusion(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error cleaning cache"
        mock_run.return_value = mock_result
        
        result = linux_agent.clean_system.invoke({})
        self.assertIn("Failed: Error cleaning cache", result)

    @patch('pathlib.Path.iterdir')
    def test_reorganize_documents_case_insensitive(self, mock_iterdir):
        # We need to do a limited test as file system mocks can be complex,
        # but we can verify the fix logic
        
        # Create mock file objects
        docs = linux_agent.Path.home() / "Documents"
        docs.mkdir(parents=True, exist_ok=True)
        
        mock_file_jpg = MagicMock()
        mock_file_jpg.is_file.return_value = True
        mock_file_jpg.parent = linux_agent.Path.home() / "Documents"
        mock_file_jpg.name = "test.JPG"
        mock_file_jpg.suffix = ".JPG"
        mock_file_jpg.stem = "test"
        
        mock_iterdir.return_value = [mock_file_jpg]
        
        with patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('pathlib.Path.rename') as mock_rename:
            
            result = linux_agent.reorganize_documents.invoke({})
            
            # Should match the "Images" category despite being upper case
            self.assertIn("test.JPG -> Images/", result)
            mock_file_jpg.rename.assert_called_once()

    def test_error_detector(self):
        detector = linux_agent.ErrorDetector()
        
        cat, pat = detector.detect("dpkg: error processing package")
        self.assertEqual(cat, "package")
        
        cat, pat = detector.detect("bind: permission denied")
        self.assertEqual(cat, "permission")

        cat, pat = detector.detect("Some random unknown error that isn't matched")
        self.assertEqual(cat, "unknown")

if __name__ == '__main__':
    unittest.main()
