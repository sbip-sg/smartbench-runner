#!/usr/bin/env python3

"""
Module handling Solc
"""

# Standard Library
import json
import os
import shlex
import subprocess
import sys

from subprocess import PIPE, Popen
from typing import List, Optional

# Third Party
import nodesemver
import solc_detect

from solc_json_parser.parser import SolidityAst

# Library
from smartbench.printer import debug, error_traceback


SMARTBENCH_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def install_solc_maybe(version) -> str:
    """Install a new Solc compiler for a given version using `solc-select`."""

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


def configure_local_solc_path(test_file: str) -> str:
    """Configure Solc compiler for a test file.

    Return path to the required Solc compiler."""
    version = detect_required_solc_version(test_file)
    install_solc_maybe(version)

    # Find path to the Solc compiler installed by solc-select
    pyenv_dir = os.getenv("VIRTUAL_ENV")
    if pyenv_dir is None:
        pyenv_dir = os.getenv("HOME")
    solc_name = f"solc-{version}"
    solc_dir = os.path.join(pyenv_dir, ".solc-select/artifacts", solc_name)
    solc_path = os.path.join(solc_dir, solc_name)
    debug(f"Using Solc: {solc_path}")
    return solc_path


def get_candidate_testing_contracts(
    test_file: str,
    only_deployable_contracts: bool = True,
    solc_version: Optional[str] = None,
) -> List[str]:
    """Detect Solidity version in a smart contacts."""

    try:
        if solc_version is None:
            solc_version = detect_required_solc_version(test_file)
        debug(f"Get contract names using Solc version: {solc_version}")
    except Exception:
        error_traceback(f"Failed to detect Solc version: {test_file}")
        return []

    try:
        if nodesemver.satisfies(solc_version, ">=0.4.11"):
            # Get contract names using Solc json parser
            ast = SolidityAst(test_file, version=solc_version)

            contract_names = ast.all_contract_names
            if only_deployable_contracts:
                abstract_contracts = ast.all_abstract_contract_names
                contract_names = [
                    x for x in contract_names if x not in abstract_contracts
                ]

            debug(f"Solj JSON parser: target contract names: {contract_names}")
            return contract_names
    except Exception:
        try:
            # Get contract names using Solquery
            cmd = f"{SMARTBENCH_ROOT}/solquery -q get-name {test_file}"
            if only_deployable_contracts:
                cmd += " --deployable-contracts"
            else:
                cmd += " --all-contracts"

            result = subprocess.run(
                shlex.split(cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )

            contract_names = result.stdout.decode("utf-8").strip().split(" ")
            contract_names = [name for name in contract_names if name]

            debug(f"Solquery: target contract names: {contract_names}")
            return contract_names
        except Exception:
            error_traceback(f"Failed to get contract names from: {test_file}")
            return []
