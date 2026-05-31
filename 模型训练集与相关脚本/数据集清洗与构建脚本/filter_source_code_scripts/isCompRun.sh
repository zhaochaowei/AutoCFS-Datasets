for dir in data*/; do
	for file in ${dir}/*; do
		#echo $file
		cp -r $file ./train
	done
done
