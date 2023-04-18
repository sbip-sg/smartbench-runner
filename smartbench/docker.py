#!/usr/bin/env python3

# Standard Library
import os
import shlex
import subprocess

from subprocess import CalledProcessError
from typing import Dict, List, Optional

# Library
from smartbench.printer import debug, error, error_traceback, safe_print


# Init some paths
SMARTBENCH_ROOT = os.path.dirname(os.path.dirname(__file__))
DOCKER_INSTALLER = "install-tool-docker.sh"


class DockerContainer:
    """Class modelling a docker container for a job"""

    def __init__(self, name: str):
        self.name = name.lower()

    def __str__(self) -> str:
        return f"{self.name}"

    def start(self) -> None:
        """Start the docker container"""
        command = f"docker start {self.name}"
        try:
            safe_print(f"Starting docker container: {self}")
            subprocess.run(
                shlex.split(command),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except CalledProcessError as err:
            error(f"Failed to start Docker container: {self}!\n")
            raise err

    def stop(self) -> None:
        """Stop the docker container"""
        command = f"docker stop {self.name}"
        try:
            safe_print(f"Stopping docker container: {self}")
            subprocess.run(
                shlex.split(command),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except CalledProcessError as err:
            error(f"Failed to stop Docker container: {self}!\n")
            raise err


def install_docker_containers(tool_id: str, num_containers: int) -> bool:
    "Install docker containers. Return `True` if the installation succeeds."
    # Prepare command to install docker containers
    cmd = os.path.join(SMARTBENCH_ROOT, DOCKER_INSTALLER)
    cmd += f" -t {tool_id} -n {num_containers} --force-install"

    debug(f"Command: {cmd}")

    try:
        with subprocess.Popen(
            shlex.split(cmd),
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            shell=False,
        ) as proc:
            # Install Docker
            (stdout, _) = proc.communicate()
            return True
    except Exception:
        error_traceback(f"Failed to install docker container: {cmd}")
        return False
