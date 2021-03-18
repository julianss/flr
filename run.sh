#/bin/bash
python3 prestart.py $1 & SCHPID=$!
python3 main.py $1
kill $SCHPID
