#!/bin/bash
project_name="$1"
run_coverage.pl -p "$project_name" -d evosuite/generated_tests/"$project_name"/evosuite/1 -o evosuie_coverages

