for dir in $1;do
	if [ -z "$(ls -A "$dir")" ];then
		echo "空目录：${dir}"
		ls "${dir}"
	fi
done
