#!/bin/bash

replica_num=$1
config_file=$2
loss_rate=$3
skip=$4
fail=$5

for ((i=0;i<${replica_num};i=i+1))
do
    python3 run_replica_manual.py ${config_file} --rid=${i} --p=${loss_rate} --skip=${skip} --fail=${fail}  &
done