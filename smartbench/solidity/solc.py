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
from typing import List, Optional, Tuple

# Third Party
import nodesemver
import solc_detect

#from solc_json_parser.parser import SolidityAst
from solc_json_parser.combined_json_parser import CombinedJsonParser

# Library
from smartbench.printer import debug, error_traceback, safe_print, warning


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
    # safe_print("Current version:", current_version)
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
        safe_print("Installing Solc", version)
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
        safe_print("Unable to install the required Solc:", version)
        sys.exit()


def detect_best_solc_versions(test_file: str) -> List[str]:
    """Detect best Solc versions to compile the input smart contacts."""
    pragma = solc_detect.find_pragma_solc_version(test_file)
    best_versions = solc_detect.find_all_best_solc_versions_for_pragma(pragma)
    return best_versions


def get_target_contracts_and_solc_version(
    test_file: str,
    only_deployable_contracts: bool = True,
    solc_version: Optional[str] = None,
) -> Tuple[List[str], Optional[str]]:
    """Collect target contracts and the suitable Solc version to compile
    the input test file."""

    try:
        if solc_version is None:
            best_solc_versions = detect_best_solc_versions(test_file)
            debug(f"Best Solc versions auto-detected: {best_solc_versions}")
        else:
            debug(f"Solc version specfied from CLI: {solc_version}")
            best_solc_versions = [solc_version]
    except Exception:
        error_traceback(f"Failed to detect best Solc versions: {test_file}")
        return []

    # First, try to get target contracts name using `solc_json_parser`, since
    # the underlying library `py-solc-x` is also used by other tools. If
    # `solc_json_parser` can to compile the contracts, then other tools will
    # also likely to be able to compile the contracts
    ast = None

    # Run SolcJSONParser with different solc versions
    for solc_version in best_solc_versions:
        try:
            ast = CombinedJsonParser(test_file, version=solc_version)
            # ast = SolidityAst(test_file, version=solc_version)
            if ast is not None:
                break
        except Exception as err:
            error_traceback(f"Exception while compiling {test_file}:\n\n{err} solc version: {type(solc_version)}")
            pass

    # Get contract information from AST parsed by SolcJSONParser
    if ast is not None:
        contracts = ast.all_contract_names
        if only_deployable_contracts:
            library_names = ast.all_libraries_names
            abstract_contracts = ast.all_abstract_contract_names
            contracts = [
                s
                for s in contracts
                if s not in abstract_contracts and s not in library_names
            ]

        debug(f"Target contracts (found by SolcJsonParser): {contracts}")

        debug(f"Using Solc: {solc_version}")
        return (contracts, solc_version)

    # If `SolcJsonParser` fails to get contract names, then use `SolQuery` to
    # try get contract names by trying each of the detected best Solc versions.
    for solc_version in best_solc_versions:
        try:
            cmd = f"{SMARTBENCH_ROOT}/bin/solquery -q get-name {test_file}"
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

            contracts = result.stdout.decode("utf-8").strip().split(" ")
            contracts = [name for name in contracts if name]

            debug(f"Target contracts (found by SolQuery): {contracts}")

            debug(f"Using Solc: {solc_version}")
            return (contracts, solc_version)
        except Exception:
            pass

    # Report an error if no contract names are found
    error_traceback(f"Failed to get contract names from: {test_file}")
    return ([], None)
