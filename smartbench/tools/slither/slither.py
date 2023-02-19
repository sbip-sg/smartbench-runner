#!/usr/bin/env python3

"""Module handling Slither."""

# Standard Library
import os

# Third Party
import toml


SLITHER = "slither.toml"


def read_slither_configuration():
    module_path = __file__
    dir_path = os.path.dirname(module_path)
    print("Path: " + module_path)
    print("Dir: " + dir_path)
    config_file_path = os.path.join(dir_path, SLITHER)
    with open(config_file_path, "r", encoding="utf-8") as file:
        cfg_data = file.read()
        cfg_toml = toml.loads(cfg_data)
        print("CFG: " + str(cfg_toml))
