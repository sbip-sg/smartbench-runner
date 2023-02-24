#!/usr/bin/env python3

# Standard Library
import os
import sys

# Third Party
import toml

# Library
import smartbench


def make_output_dir(tool_id: str, test_file: str, result_dir: str):
    """Make output directory of a tool for a test file."""

    # Prepare output directory
    test_name = os.path.basename(test_file)
    output_dir = os.path.join(result_dir, tool_id, test_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return output_dir
