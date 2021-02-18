#!/bin/bash

client_num=$1
config_file=$2
loss_rate=$3
m=$4

for ((i=0;i<${client_num};i=i+1))
do
    python3 run_client_manual.py ${config_file} --cid=${i} --p=${loss_rate} --m=${i}  &
done