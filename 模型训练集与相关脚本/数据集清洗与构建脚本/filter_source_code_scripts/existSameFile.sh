find data* -type f -name "*.cpp" -printf "%f\n" | sort | uniq -c | sort -nr | awk '$1 > 1' > existSameFile.log
