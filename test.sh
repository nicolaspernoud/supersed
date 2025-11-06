#!/bin/bash

rm -rf ./test_dir

mkdir -p test_dir/initialname_dir test_dir/another_dir
echo "This is a file about initialname. initialname is a great tool. initialname is awesome." > test_dir/initialname_dir/initialname_file.rs
echo "This file does not contain the term." > test_dir/initialname_dir/another_file.rs
echo "This is a log file for initialname. initialname Agent is running. initialname-agentd is also running." > test_dir/another_dir/initialnameFile.log
echo '{ "name": "initialname Project", "version": "1.0" }' > test_dir/another_dir/data.json
echo "This is a root file about initialname. initialname Agent: active initialname-agentd: inactive" > test_dir/root_initialname_file.rs
mv test_dir/another_dir/initialnameFile.log test_dir/another_dir/initialname_file.log
mv test_dir/initialname_dir/initialname_file.rs test_dir/initialname_dir/initialname_file.rs
mv test_dir/root_initialname_file.rs test_dir/root_initialname_file.rs
mv test_dir/initialname_dir test_dir/initialname_dir

python3 rename.py ./test_dir/ initialname newname
