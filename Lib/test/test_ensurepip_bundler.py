import sys
import tempfile
import unittest
import unittest.mock
import urllib.request
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from random import randbytes
from test import test_tools, support
from test.test_ensurepip import EnsurepipMixin

import ensurepip

test_tools.skip_if_missing('build')
with test_tools.imports_under_tool('build'):
    from bundle_ensurepip_wheels import _wheel_url, download_pip_wheel


class TestBundle(EnsurepipMixin, unittest.TestCase):
    contents = randbytes(512)
    checksum = sha256(contents).hexdigest()

    def test__wheel_url(self):
        self.assertEqual(
            _wheel_url('pip', '1.2.3'),
            'https://files.pythonhosted.org/packages/py3/p/pip/pip-1.2.3-py3-none-any.whl'
        )

    def test_invalid_checksum(self):
        class MockedHTTPSOpener:
            @staticmethod
            def open(url, data, timeout):
                assert 'pip' in url
                assert data is None  # HTTP GET
                # Intentionally corrupt the wheel:
                return BytesIO(self.contents[:-1])

        with (
            support.captured_stderr() as stderr,
            unittest.mock.patch.object(urllib.request, '_opener', None),
            unittest.mock.patch.object(ensurepip, '_PIP_SHA_256', self.checksum),
        ):
            urllib.request.install_opener(MockedHTTPSOpener())
            download_pip_wheel()
        stderr = stderr.getvalue()
        self.assertIn("Failed to validate checksum for", stderr)

    def test_cached_wheel(self):
        pip_filename = "pip-1.2.3-py3-none-any.whl"

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, pip_filename).write_bytes(self.contents)
            with (
                support.captured_stderr() as stderr,
                unittest.mock.patch.object(ensurepip, '_PIP_VERSION', '1.2.3'),
                unittest.mock.patch.object(ensurepip, '_PIP_SHA_256', self.checksum),
            ):
                download_pip_wheel()
            stderr = stderr.getvalue()
            self.assertIn("A valid 'pip' wheel already exists!", stderr)

    def test_download_wheel(self):
        pip_filename = "pip-1.2.3-py3-none-any.whl"

        class MockedHTTPSOpener:
            @staticmethod
            def open(url, data, timeout):
                assert 'pip' in url
                assert data is None  # HTTP GET
                return BytesIO(self.contents)

        with tempfile.TemporaryDirectory() as tmpdir:
            with (
                support.captured_stderr() as stderr,
                unittest.mock.patch.object(urllib.request, '_opener', None),
                unittest.mock.patch.object(ensurepip, '_PIP_VERSION', '1.2.3'),
                unittest.mock.patch.object(ensurepip, '_PIP_SHA_256', self.checksum),
            ):
                urllib.request.install_opener(MockedHTTPSOpener())
                download_pip_wheel()
            self.assertEqual(Path(tmpdir, pip_filename).read_bytes(), self.contents)
        stderr = stderr.getvalue()
        self.assertIn("Downloading 'pip-1.2.3-py3-none-any.whl'", stderr)
        self.assertIn("Writing 'pip-1.2.3-py3-none-any.whl' to disk", stderr)
