#find /home/xinda/selectingComOpts-O3/src/train_real_compilable/temp/filtered_gimple -type f -name "*tester.cpp" | xargs sed -i 's/clock_t begin = clock();/uint64_t begin = get_tc();/g'
#find /home/xinda/selectingComOpts-O3/src/train_real_compilable/temp/filtered_gimple -type f -name "*tester.cpp" | xargs sed -i 's/clock_t end = clock();/uint64_t end = get_tc();/g'
#find /home/xinda/selectingComOpts-O3/src/train_real_compilable/temp/filtered_gimple -type f -name "*tester.cpp" | xargs sed -i 's|(double)(end - begin) / CLOCKS_PER_SEC|end - begin|g'
for file in $(find . -type f -name "*tester.cpp"); do
#    if ! grep -q "#include.*stdint.h" "$file"; then
#        sed -i '1i #include <stdint.h>' "$file"
#    fi
        sed -i '1i #include "/home/xinda/time_test.cpp"' "$file"
done
