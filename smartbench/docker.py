#!/usr/bin/env python3

# Standard Library
import os
import shlex
import subprocess

from subprocess import CalledProcessError
from typing import Dict, List, Optional

# Third Party
import docker

# Library
from smartbench import printer
from smartbench.printer import debug, error, error_traceback, safe_print


# Init some paths
SMARTBENCH_ROOT = os.path.dirname(os.path.dirname(__file__))
SCRIPTS_DIR = os.path.join(SMARTBENCH_ROOT, "scripts")
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


def install_docker_containers(
    tool_id: str,
    num_containers: int,
    use_local_images: bool = True,
    only_create_containers: bool = False,
) -> bool:
    """Build and install docker containers locally. Return `True` if the
    installation succeeds."""

    # Prepare command to install docker containers
    cmd = os.path.join(SCRIPTS_DIR, DOCKER_INSTALLER)
    cmd += f" -t {tool_id} -n {num_containers} --force-install"

    if only_create_containers:
        cmd += " --only-create-containers"
    elif not use_local_images:
        cmd += " --use-remote-images"

    debug(f"COMMAND: {cmd}")

    try:
        subprocess.run(
            shlex.split(cmd),
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except Exception as err:
        error_traceback(f"Failed to install docker container: {cmd}\n{err}")
        return False
