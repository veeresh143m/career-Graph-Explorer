import os
import unittest

from db import CognoDBClient


class FallbackClientTests(unittest.TestCase):
    def test_fallback_client_works_without_database_credentials(self):
        os.environ.pop("COGNODB_URI", None)
        os.environ.pop("COGNODB_PASSWORD", None)
        os.environ.pop("COGNODB_USER", None)

        client = CognoDBClient()
        self.assertIn("Data Analyst", client.list_roles())
        self.assertIn("Python", client.list_skills())

        details = client.get_skill_details("Python")
        self.assertEqual(details["name"], "Python")
        self.assertTrue(details["courses"])

        client.close()


if __name__ == "__main__":
    unittest.main()
