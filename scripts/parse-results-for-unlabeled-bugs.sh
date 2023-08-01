#!/bin/bash

for i in {1..3}
do
    find benchmarks/ -type f -name '*smartfuzz_stats.csv' -delete
    rm *.json

    ./smartbench.sh parse-results -r results/test_finals/verismartpp_final/run$i  -t smartfuzz --annot-format verismart --validate --disable-print-details
    ./smartbench.sh parse-results -r results/test_finals/solidifipp_final/run$i  -t smartfuzz --annot-format solidifi --validate --disable-print-details
    ./smartbench.sh parse-results -r results/test_finals/smartbugpp-final/run$i  -t smartfuzz --annot-format smartbugs --validate --disable-print-details
    ./smartbench.sh parse-results -r results/usenix_realhack_final/run$i  -t smartfuzz --annot-format smartbench --validate --disable-print-details

    # (find . -maxdepth 1 -type f -name '*.json' -print0; find benchmarks/ -type f -name '*smartfuzz_stats.csv' -print0) | xargs -0 7z a run$i.7z

    mkdir -p run$i
    find . -maxdepth 1 -type f -name '*.json' -print0 | xargs -0 -I {} rsync -R {} ./run$i/
    find benchmarks/ -type f -name '*smartfuzz_stats.csv' -print0 | xargs -0 -I {} rsync -R {} ./run$i/
done
