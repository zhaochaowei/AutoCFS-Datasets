mkdir -p filtered_gimple

find . -name "*.gimple" -print0 | parallel -0 -j100 '
	f={};
	lines=$(grep -v -e "^[[:space:]]*;" -e "^[[:space:]]*$" "$f" | wc -l);
	[ $lines -gt 10 ] &&  echo "$f" | tee -a fg.log

'

cat fg.log | awk -F'.c.006t.gimple' '{print $1}' | xargs -I {} cp -r --parents  {} ./filtered_gimple/

echo "$(ls -1 ./filtered_gimple/*/*/*impl.c | wc -l)"
