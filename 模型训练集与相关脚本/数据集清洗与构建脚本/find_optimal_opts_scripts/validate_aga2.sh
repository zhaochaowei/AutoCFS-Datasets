src_path="/home/xinda/selectingComOpts-O3/src/filtered_gimple_500c"


#find $src_path -name "*tester.cpp" | while read -r f; do
#sed -n '1,128p' input.txt | while read -r f; do
cat input.txt.1786 | while read -r f; do
	dir=$(dirname $f)
	name=$(basename $dir)
	base_log=${dir}/base.log
	aga_log=${dir}/aga.log
	base_time=$(sed -n 's|^Time: ||gp' $base_log | sort -n | awk '{if (NR>3 && NR<10) print last; last=$0}' | awk '{sum += $1} END {print sum/6}')
	aga_time=$(sed -n 's|^Time: ||gp' $aga_log | sort -n | awk '{if (NR>3 && NR<10) print last; last=$0}' | awk '{sum += $1} END {print sum/6}')
	echo "$f $base_time $aga_time" >> t1.log

done
#echo "base aga speed_clock speed_percentage"
#awk -F' ' '{print $2,$3,$2-$3,($2-$3)/$2}' v1.log  >> v2.log
#awk  '$4 > 0 {sum+=$4;count++} END {print "speedup" "\ncount:",count "\nmean:",sum/count} ' v2.log
#awk  '$4 <= 0 {sum+=$4;count++} END {print "\nspeeddown" "\ncount:",count "\nmean:",sum/count} ' v2.log
#awk  '$2-$3 <= 0 {count++} END {print "\nspeeddown" "\ncount:",count} ' sd1.log
#awk  '$2-$3 <= 0' sd1.log > sd2.log

#awk -F' ' '{print ($2-$3)/$2}' sd1.log  >> sd2.log
