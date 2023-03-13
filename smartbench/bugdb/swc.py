#!/usr/bin/env python3

"""Module handling smart contract SWCs."""

# Standard Library
import json
import os

from dataclasses import dataclass
from enum import Enum
from typing import List


SMARTBENCH_DIR = os.path.dirname(__file__)
PROJECT_ROOT_DIR = os.path.dirname(SMARTBENCH_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT_DIR, "data")


@dataclass
class SWC:
    """Class modelling a SWC."""

    # Attributes
    id: str
    title: str
    description: str
    remediation: str
    relationships: List[str]
    reference: str


if __name__ == "__main__":
    print(f"Smartbench dir: {SMARTBENCH_DIR}")
    print(f"Data dir: {DATA_DIR}")

    swc_file = os.path.join(DATA_DIR, "swc.json")

    with open(swc_file, "r", encoding="utf-8") as file:
        try:
            swcs = json.load(file, object_hook=lambda obj: SWC(**obj))
            print(f"#SWCs: {len(swcs)}")
            for swc in swcs:
                print(f"- {swc.id}: {swc.title}")
        except ValueError:
            print("Failed to parse SWC file:", swc_file)

    if swcs is None:
        print("Failed to parse SWC file:", swc_file)


class SWCKind(Enum):
    """Class modelling a SWC Kind"""
