import argparse
import multiprocessing
import os
import pathlib
import shlex
import subprocess
from multiprocessing import Process, Queue

SMARTBENCH_ROOT = os.path.dirname(__file__)


def find_test_files_in_directory(directory: str):
    """
    Find all Solidity files in a directory.
    Return a list of absolute file names.
    """
    files = []
    path = pathlib.Path(directory)
    for file_path in path.rglob("*"):
        file_name = os.path.normpath(os.path.abspath(file_path))
        if file_name[-4:] in (".sol"):
            files.append(file_name)
    return files


def parse_cli_arguments():
    """Configure command arguments line."""
    arg_parser = argparse.ArgumentParser(
        description="Detect Solidity compiler version for a smart contract",
        add_help=True,
    )

    # Input files or directories
    arg_parser.add_argument(
        "input_files_directories",
        nargs="*",  # Accept multiple result directories
        type=str,
        help="Input files or directories for testing.",
    )

    # Number of jobs per tool
    arg_parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        help="Number of jobs to be run concurrently for each tool.",
    )

    return arg_parser.parse_args()


def run_solquery(test_files):
    for test_file in test_files:
        # Run `solquery` to get contract names
        cmd = f"./solquery -q get-name {test_file}"
        cmd += " --deployable-contracts"

        result = subprocess.run(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        print(f"{test_file}: Solquery output:", result.stdout.decode("utf-8").strip())

        contract_names = result.stdout.decode("utf-8").strip().split(" ")
        contract_names = [name for name in contract_names if name]

        print(f"Target contract names: {contract_names}")


def main():
    args = parse_cli_arguments()

    test_files = []
    for input_path in args.input_files_directories:
        if os.path.isdir(input_path):
            test_files += find_test_files_in_directory(input_path)
        elif os.path.isfile(input_path):
            input_path = os.path.abspath(input_path)
            if input_path[-4:] in (".sol"):
                test_files.append(input_path)

    test_batches = []
    jobs = 1 if args.jobs is None else args.jobs
    for _ in range(jobs):
        test_batches.append([])

    for idx, test_file in enumerate(test_files):
        idx = idx % jobs
        test_batches[idx].append(test_file)

    # print("Test batches: ", test_batches)

    processes = []
    for batch in test_batches:
        proc = Process(target=run_solquery, args=(batch,))
        processes.append(proc)
        proc.start()

    for proc in processes:
        proc.join()


if __name__ == "__main__":
    main()
