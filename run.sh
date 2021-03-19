#/bin/bash
python3 load_db.py $1 
python3 sched.py $1 & echo $! > scheduler.pid
python3 main.py $1
