#!/usr/bin/env python3

# Standard Library
import os
import sys

# Third Party
import toml

# Library
import smartbench


def get_output_directory(tool_id: str, test_file: str, result_dir: str):
    """
    Get output directory of a tool for a test file.
    Create a new one if it does not exists.
    """

    # Prepare output directory
    test_name = os.path.basename(test_file)
    output_dir = os.path.join(result_dir, tool_id, test_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return output_dir
