src_path="/home/xinda/selectingComOpts-O3/src/filtered_gimple_500c"
#find $src_path -type f -name "*tester.cpp" -print0 | parallel -0 -j120 '
#sed -n '1,128p' input.txt | parallel -j120 '
cat input.txt.1786 | parallel -j128 '
	compile_cmd="sw_64-sunway-linux-gnu-g++ -O3 -static -std=c++11"
	f={};
        dir=$(dirname $f);

	input=${dir}/input.json;
	
	binary_base=${dir}/base.out;
	log_base=${dir}/base.log;
	
	binary_aga=${dir}/aga.out;
	log_aga=${dir}/aga.log;
	
	$compile_cmd $f -o $binary_base;
	
	$binary_base $input > $log_base;
	for(( i=0;i<9;i++ )); do
		$binary_base $input >> $log_base;
	done

	#flag_path=$(echo ${dir} | sed "s|filtered_gimple_500c|log|g")/output.log;
	flag_path=${dir}/output.log
	flag=$(sed -n "3s|^Best Compiler Options: ||p" $flag_path);

	$compile_cmd $flag $f -o $binary_aga;
        
	$binary_aga $input > $log_aga;
	for(( i=0;i<9;i++)); do
		$binary_aga $input >> $log_aga;
	done
'

