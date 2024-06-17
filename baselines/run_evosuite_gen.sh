#!/bin/bash

# 第一个参数是项目名称
project_name="$1"

# 使用 shift 命令移除第一个参数，剩下的参数都是数字
shift

# 使用 "$@" 获取剩余的所有命令行参数（即数字）
for number in "$@"; do
#    echo -g evosuite -p "$project_name" -v "$number"f -n 1 -o evosuite/generated_tests -b 120
    # 使用项目名称和数字作为 gen_tests.pl 的参数
    gen_tests.pl -g evosuite -p "$project_name" -v "$number"f -n 1 -o evosuite/generated_tests -b 120
done

