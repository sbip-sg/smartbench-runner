import json
import os
from collections import defaultdict



stats_types = ['smartfuzz_smartbench_global_stats.json',
               'smartfuzz_smartbugs_global_stats.json',
               'smartfuzz_solidifi_global_stats.json',
               'smartfuzz_verismart_global_stats.json']

for f_stat in stats_types:
    files = [f'run{i}/{f_stat}' for i in range(1, 4)]

    # Initialize an empty dictionary to store the sums
    sums = defaultdict(lambda: defaultdict(int))

    # Initialize an empty dictionary to store the counts
    counts = defaultdict(lambda: defaultdict(int))

    # Loop over each file
    for file in files:
        # Open the file and load the JSON data
        with open(file, 'r') as f:
            data = json.load(f)

        # Loop over each key-value pair in the data
        for key, value in data.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    # Add the value to the sum for that key
                    sums[key][subkey] += subvalue

                    # Increment the count for that key
                    counts[key][subkey] += 1
            else:
                # Add the value to the sum for that key
                sums[key]["value"] += value

                # Increment the count for that key
                counts[key]["value"] += 1

    # Initialize an empty dictionary to store the averages
    averages = defaultdict(dict)

    # Loop over each key in the sums dictionary
    for key in sums:
        for subkey in sums[key]:
            # Calculate the average for that key
            averages[key][subkey] = sums[key][subkey] / counts[key][subkey]

    # Print the averages
    with open(f'avg_{f_stat}', 'w') as f:
        f.write(json.dumps(averages, indent=4))
