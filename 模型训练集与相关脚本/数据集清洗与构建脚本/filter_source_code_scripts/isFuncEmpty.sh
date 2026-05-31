#find -name "*impl.c"
mapfile -t func_array < <(find . -type f -name "*impl.c")
index=0
for func in "${func_array[@]}"; do
	dir=$(echo ${func} | awk -F'/' '{print $2}')
	file=$(echo ${func} | awk -F'/' '{print $3}')
	mkdir -p ./temp/$dir
	sw_64-sunway-linux-gnu-g++ -O0 -static -c -fdump-tree-gimple -dumpdir ./temp/${dir}/ $func -o ./temp/${dir}/${file}.o
	let index++
done
echo "sum of gimple: ${index}"
