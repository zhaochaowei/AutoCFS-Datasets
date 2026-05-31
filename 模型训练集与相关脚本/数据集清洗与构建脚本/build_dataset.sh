#!/bin/bash

# 提取出最优编译选项组合对应的0-1二值向量-"output.log.filtered"
dataset_path="/home/xinda/selectingComOpts-O3/src/filtered_gimple_500c"
find ${dataset_path} -name "output.log" > temp_output.log

cat temp_output.log | while read -r file; do
  sed -n "2,2p" "$file" | awk -F': ' '{print $2}' > "${file}.filtered"
done

# 编译所有的_impl.c文件生成其gimple形式-"<name>_impl.c.006t.gimple"
# 处理每一行并执行编译命令
while IFS= read -r line; do
    # 提取目录路径
    dir_path=$(dirname "$line")

    # 提取文件名（不带路径）
    file_name=$(basename "$dir_path")

    # 构造编译命令
    compile_command="sw_64-sunway-linux-gnu-g++ -O0 -fdump-tree-gimple -c $dir_path/${file_name}_impl.c -o $dir_path/${file_name}_impl.o"

    # 输出并执行命令
    echo "执行: $compile_command"
    $compile_command

    # 检查执行结果
    if [ $? -eq 0 ]; then
        echo "✓ 编译成功"
    else
        echo "✗ 编译失败"
    fi
    echo ""
done < temp_output.log

# 将个源码对应的gimple形式及其最优编译选项组构造成csv文件
# 1. 初始化CSV文件
csv_file="gimple_optimizations.csv"
echo "gimple_code,optimization_vector" > "$csv_file"

# 2. 遍历所有目录
cat temp_output.log | while read -r dir; do
    # 3. 获取目录名（作为标识）
    dir_name=$(dirname "$dir")
    base_name=$(basename "$dir_name")
    # 4. 查找GIMPLE文件
    gimple_file=${dir_name}/${base_name}_impl.c.006t.gimple

    # 5. 查找优化向量文件
    opt_vector_file="${dir_name}/output.log.filtered"

    # 6. 检查文件存在性
    if [[ -f "$gimple_file" && -f "$opt_vector_file" ]]; then
        # 7. 读取GIMPLE文件内容
        gimple_content=$(cat "$gimple_file")

        # 8. 处理特殊字符（CSV转义）
        gimple_content_escaped=$(echo "$gimple_content" | sed 's/"/""/g' | tr '\n' ' ')

        # 9. 读取优化向量
        opt_vector=$(cat "$opt_vector_file" | tr -d '\n')

        # 10. 添加到CSV
        echo "\"$gimple_content_escaped\",\"$opt_vector\"" >> "$csv_file"
        echo "已添加: $dir_name"
    else
        echo "警告: $dir_name 缺少文件 (GIMPLE: $gimple_file, 优化: $opt_vector_file)"
    fi
done

echo "CSV 文件已生成: $csv_file"
echo "记录数量: $(($(wc -l < "$csv_file") - 1))"  # 减去标题行
