#!/usr/bin/env python3

"""Module to test analysis tools using Pytest"""

# Standard Library
import os

# Library
from smartbench import analyze
from smartbench.tools import config


TESTING_DIR = os.path.realpath(os.path.dirname(__file__))
SMARTBENCH_ROOT = os.path.dirname(TESTING_DIR)
EXAMPLE_DIR = os.path.join(SMARTBENCH_ROOT, "examples")

TEST_FILES = [
    os.path.join(EXAMPLE_DIR, "BecToken.sol"),
    os.path.join(EXAMPLE_DIR, "all_bug_sample_0_4.sol"),
    os.path.join(EXAMPLE_DIR, "all_bug_sample_0_7.sol"),
]


def test_slither():
    slither = config.load_tool_configuration("slither")

    analysis_results = analyze.perform_analysis(
        [slither], TEST_FILES, jobs=1, validate=False
    )

    assert len(analysis_results) == len(TEST_FILES)


def test_mythril():
    mythril = config.load_tool_configuration("mythril")

    analysis_results = analyze.perform_analysis(
        [mythril], TEST_FILES, jobs=1, validate=False
    )

    assert len(analysis_results) == len(TEST_FILES)
