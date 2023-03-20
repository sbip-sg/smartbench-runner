#!/usr/bin/env python3

"""Module handling log file generated during the analysis."""


# Standard Library
from typing import Union

# Third Party
# import qtoml
import toml
import tomli

# Library
from smartbench.debug import warning


def get_input_test_file(log_file: str) -> Union[str, None]:
    """Get input test file from a log file"""
    print(f"log_file: {log_file}")
    with open(log_file, "r", encoding="utf-8") as file:
        file_content = file.read()
        try:
            log = toml.loads(file_content)
        except:
            log = tomli.loads(file_content)

        input_log = log.get("input")
        if input_log is None:
            warning("Invalid log file! No input information is found!")
            return None

        return input_log.get("test_file")
