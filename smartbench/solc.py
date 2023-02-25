#!/usr/bin/env python3

"""
Module handling Solc
"""


# Standard Library
import subprocess
import sys

# Third Party
import solc_detect


def install_solc_maybe(version):
    """Install a new Solc compiler for a given version using solc-select.

    The $HOME folder of  solc-select is `smartbugs/venv`.
    """
    # Check current Solc version
    version = str(version).strip()
    result = subprocess.run(
        ["solc", "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    current_version = result.stdout.decode("utf-8")
    # print("Current version:", current_version)
    if version in current_version:
        return

    # Install the required version
    result = subprocess.run(
        ["solc-select", "versions"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    installed_versions = result.stdout.decode("utf-8")
    if not (version in installed_versions):
        print("Installing Solc", version)
        subprocess.run(
            ["solc-select", "install", version],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    # Configure the required version
    subprocess.run(
        ["solc-select", "use", version],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    # Verify Solc version
    result = subprocess.run(
        ["solc", "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    current_version = result.stdout.decode("utf-8")
    if not (version in current_version):
        print("Unable to install the required Solc:", version)
        sys.exit()


def detect_required_solc_version(test_file: str) -> str:
    """Detect Solidity version in a smart contacts"""
    pragma = solc_detect.find_pragma_solc_version(test_file)
    best_version = solc_detect.find_best_solc_version_for_pragma(pragma)
    return best_version


def configure_solc_compiler(test_file: str):
    """Configure Solc compiler for a test file."""
    best_version = detect_required_solc_version(test_file)
    install_solc_maybe(best_version)
