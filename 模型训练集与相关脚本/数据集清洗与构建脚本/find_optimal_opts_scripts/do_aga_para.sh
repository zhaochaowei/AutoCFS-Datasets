# $1=/home/xinda/selectingComOpts-O3/src/filtered_gimple_500c

# binding cores number for every program's adaptive-gene-algorithem
cores=127
rm core_list_long.txt
#find $1 -type f -name "*tester.cpp" > input.txt
seq 0 $cores > core_list.txt
lines=$(wc -l < input.txt)
repeat_times=$(( (lines - 1) / cores + 1 ))
for i in $(seq 1 $repeat_times);do
	cat core_list.txt >> core_list_long.txt
done

paste core_list_long.txt input.txt > input_with_cores.txt
sed -i "$(( lines+1 )),\$d" input_with_cores.txt

# runing all programs in single core
#find /home/xinda/selectingComOpts-O3/src/filtered_gimple_500c -type f -name "*tester.cpp" | xargs -I {} python3 aga.py {}

# runing all programs in multi cores using
parallel -j 128 --colsep '\t' 'taskset -c {1} python3 aga.py {2}' :::: input_with_cores.txt
