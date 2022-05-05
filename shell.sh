#!/bin/sh
git clone https://github.com/mkarzhaubayeva/AMT.git
cd AMT
python3 create_csv.py
FILES="./configurations/*"
STRING="measure.txt"
for f in $FILES
do
    if [[ "$f" == *"$STRING" ]]; then
        python3 main.py --only_parse --interval 100 --log_file "$f"
    fi
done