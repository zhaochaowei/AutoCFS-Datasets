#!/bin/bash

# 使用 find 命令查找所有目标文件（并行时避免使用数组直接读入）
# -print0 和 parallel 的 -0 参数处理特殊字符（如空格）
# --jobs 设置并行任务数，N 为具体的并行度（如 CPU 核心数）
find . -type f -name "*impl.c" -print0 |
parallel -0 -j100 '
    # 提取目录名：使用 dirname 和 basename 避免路径深度问题
    dir=$(echo {} | awk -F'/' '{print $2}')
    file=$(echo {} | awk -F'/' '{print $3}')
    
    # 在临时目录创建对应子目录（-p 确保目录存在）
    mkdir -p "./temp/$dir"
    
    # 执行编译命令（关键参数保持不变）
    sw_64-sunway-linux-gnu-g++ -O0 -static -c -fdump-tree-gimple \
        -dumpdir "./temp/$dir/" \
        "{}" \
        -o "./temp/$dir/${file}.o"
'

# 统计总文件数（直接复用 find 命令结果）
total=$(find . -type f -name "*impl.c" | wc -l)
echo "sum of gimple: $total"
