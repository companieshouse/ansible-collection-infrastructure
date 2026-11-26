import json
import os
import subprocess
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


RESPONSE = Path("/run/ec2-hostname-test-response.json")
SCRIPT = "/usr/local/sbin/ec2-hostname-from-tag"
BASE_URL = "http://127.0.0.1:18080/latest"


def hostname():
    return subprocess.check_output(["hostnamectl", "--static"], text=True).strip()


class HostnameTests(unittest.TestCase):
    def setUp(self):
        self.original = hostname()
        self.working_directory = Path("/run/ec2-hostname-test-body")
        self.working_directory.mkdir(exist_ok=True, mode=0o700)

    def tearDown(self):
        RESPONSE.unlink(missing_ok=True)
        subprocess.run(["hostnamectl", "set-hostname", self.original], check=True)
        self.assertEqual(list(self.working_directory.iterdir()), [])
        self.working_directory.rmdir()

    def run_script(self, config):
        RESPONSE.write_text(json.dumps(config))
        return subprocess.run(
            [SCRIPT], capture_output=True, text=True, timeout=90,
            env={**os.environ, "TMPDIR": str(self.working_directory)},
        )

    def test_valid_tag_changes_hostname(self):
        result = self.run_script({"body": "valid.example.internal"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "Hostname set to valid.example.internal")
        self.assertEqual(hostname(), "valid.example.internal")

    def test_repeat_is_idempotent(self):
        result = self.run_script({"body": self.original})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), f"Hostname already {self.original}")
        self.assertEqual(hostname(), self.original)

    def test_missing_tag_keeps_hostname(self):
        result = self.run_script({"status": 404})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            "No Hostname tag in instance metadata "
            "(either absent or metadata disabled); "
            "hostname unchanged",
        )
        self.assertEqual(hostname(), self.original)

    def test_invalid_hostname_boundaries(self):
        invalid = [
            "", "UPPER.example", "-start", "end-", "under_score", "has space",
            ".leading", "trailing.", "double..dot", "a" * 64, "a" * 65,
            "a." + "b" * 62 + ".c", "a\nb", "$(hostname)", "name;true",
        ]
        for name in invalid:
            with self.subTest(name=name):
                result = self.run_script({"body": name})
                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    "invalid (requires lowercase and <=64 characters); hostname unchanged",
                    result.stderr,
                )
                self.assertEqual(hostname(), self.original)

    def test_valid_hostname_boundaries(self):
        valid = ["a", "1", "a-b", "a" * 63, "a." + "b" * 62, "a.b"]
        for name in valid:
            with self.subTest(name=name):
                result = self.run_script({"body": name})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(hostname(), name)

    def test_token_http_error_keeps_hostname(self):
        result = self.run_script({"token_status": 403})
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"Cannot get an IMDSv2 token from {BASE_URL}", result.stderr)
        self.assertEqual(hostname(), self.original)

    def test_empty_token_keeps_hostname(self):
        result = self.run_script({"token": ""})
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"Cannot get an IMDSv2 token from {BASE_URL}", result.stderr)
        self.assertEqual(hostname(), self.original)

    def test_unexpected_http_status_keeps_hostname(self):
        result = self.run_script({"status": 403})
        self.assertEqual(result.returncode, 1)
        self.assertIn("Unexpected HTTP 403 reading Hostname tag", result.stderr)
        self.assertEqual(hostname(), self.original)

    def test_tag_transport_error_keeps_hostname(self):
        result = self.run_script({"disconnect": True})
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"Cannot read Hostname tag from {BASE_URL}", result.stderr)
        self.assertEqual(hostname(), self.original)

    def test_unreachable_metadata_keeps_hostname(self):
        subprocess.run(["systemctl", "stop", "ec2-hostname-test-imds.service"], check=True)
        try:
            result = self.run_script({})
            self.assertEqual(result.returncode, 1)
            self.assertIn(f"Cannot get an IMDSv2 token from {BASE_URL}", result.stderr)
            self.assertEqual(hostname(), self.original)
        finally:
            subprocess.run(["systemctl", "start", "ec2-hostname-test-imds.service"], check=True)

    def test_mock_requires_token_and_correct_paths(self):
        requests = [
            Request(f"{BASE_URL}/api/token", method="PUT"),
            Request(
                f"{BASE_URL}/wrong",
                method="PUT",
                headers={"X-aws-ec2-metadata-token-ttl-seconds": "60"},
            ),
            Request(f"{BASE_URL}/meta-data/tags/instance/Hostname"),
            Request(
                f"{BASE_URL}/meta-data/tags/instance/Wrong",
                headers={"X-aws-ec2-metadata-token": "ec2-hostname-test-token"},
            ),
        ]
        for request, status in zip(requests, [400, 400, 401, 404]):
            with self.subTest(path=request.full_url):
                with self.assertRaises(HTTPError) as raised:
                    urlopen(request, timeout=5)
                self.assertEqual(raised.exception.code, status)


if __name__ == "__main__":
    unittest.main(verbosity=2)
