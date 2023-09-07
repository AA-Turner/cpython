#!/usr/bin/env python3

"""
Download wheels for :mod:`ensurepip` packages from the Cheeseshop.

When GitHub Actions executes the script, output is formatted accordingly.
https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-a-notice-message
"""

import importlib.util
import os
import sys
from hashlib import sha256
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

HOST = 'https://files.pythonhosted.org'
ENSURE_PIP_ROOT = Path(__file__, "..", "..", "..", "Lib", "ensurepip").resolve()
WHEEL_DIR = ENSURE_PIP_ROOT / "_bundled"
ENSURE_PIP_INIT = ENSURE_PIP_ROOT / "__init__.py"
GITHUB_ACTIONS = "GITHUB_ACTIONS" in os.environ


def print_notice(message: str) -> None:
    if GITHUB_ACTIONS:
        print(f"::notice::{message}", end="\n\n")
    else:
        print(message, file=sys.stderr)


def print_error(message: str) -> None:
    if GITHUB_ACTIONS:
        print(f"::error::{message}", end="\n\n")
    else:
        print(message, file=sys.stderr)


def download_pip_wheel() -> int:
    """Download wheels into bundle if they are not there yet."""

    details = _get_pip_details()
    if details is None:
        print_error("Could not find '_PIP_VERSION' and '_PIP_SHA_256' in "
                    f"{ENSURE_PIP_INIT}.")
        return 1

    version, checksum = details

    wheel_filename = f'pip-{version}-py3-none-any.whl'
    wheel_path = WHEEL_DIR / wheel_filename
    if wheel_path.exists():
        if _is_valid_wheel(wheel_path.read_bytes(), checksum=checksum):
            print_notice(f"A valid 'pip' wheel already exists!")
            return 1
        else:
            print_error(f"An invalid 'pip' wheel exists.")
            os.remove(wheel_path)

    wheel_url = _wheel_url('pip', version)
    print_notice(f"Downloading {wheel_url!r}")
    try:
        with urlopen(wheel_url, cadefault=True) as response:
            whl = response.read()
    except URLError as exc:
        print_error(f"Failed to download {wheel_url!r}: {exc}")
        return 1
    if not _is_valid_wheel(whl, checksum=checksum):
        print_error(f"Failed to validate checksum for {wheel_url!r}!")
        return 1

    print_notice(f"Writing {wheel_filename!r} to disk")
    wheel_path.write_bytes(whl)
    return 0


def _get_pip_details() -> list[tuple[str, str, str]]:
    spec = importlib.util.spec_from_file_location("ensurepip", ENSURE_PIP_INIT)
    ensurepip = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ensurepip)
    try:
        return ensurepip._PIP_VERSION, ensurepip._PIP_SHA_256
    except AttributeError:
        return None


def _wheel_url(name: str, version: str, /) -> str:
    # The following code was adapted from
    # https://warehouse.pypa.io/api-reference/integration-guide.html#predictable-urls
    #
    # We rely on the fact that pip is, as a matter of policy, portable code.
    # We can therefore guarantee that we'll always have the values:
    #   build_tag = ""
    #   python_tag = "py3"
    #   abi_tag = "none"
    #   platform_tag = "any"

    # https://www.python.org/dev/peps/pep-0491/#file-name-convention
    filename = f'{name}-{version}-py3-none-any.whl'
    return f'{HOST}/packages/py3/{name[0]}/{name}/{filename}'


def _is_valid_wheel(content: bytes, *, checksum: str) -> bool:
    return checksum == sha256(content, usedforsecurity=False).hexdigest()


if __name__ == '__main__':
    raise SystemExit(download_pip_wheel())
