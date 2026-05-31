find -name *.log | xargs -I {} sed -i '/^AccTime/d' {}
find -name *.log | xargs -I {} awk '/^Time:/ {print prev, $0} !/^Time:/ {prev=$0}' {} | sort -t' ' -k3nr > {}.sorted
