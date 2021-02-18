# multi-paxos-chat-services

makre sure you run this program under the src directory

Our program didn't implement the bonus part.
Once a replica dies, It won't recover.
Our implementation can only tolerate at most f failures with 2f+1 replicas

For testing, in batch mode, we test with f=2, clients=3
in manual mode, we test with f = 1, clients = 2
all the testcases were passed from our testing

# Client message sending:
Each client have a message file to read message from and send to the primary.

You can modify these message file to send different message

# Consistency Check:
We maintain a separet log file for each replica under /logs.

To check consistency, you can open either the log file or
check consistency via running ``` check_consistency.sh ``` script.

We print the md5 hash of each log file.

# Testcases

### 1. Normal operation

no message loss

run batch mode

server
```
python3 run_replica_batch.py ../config/config2.json 
```
client  
```
python3 run_client_batch.py ../config/config2.json
```

### 2. Deal with 1 primary failure
run batch mode

server
```
python3 run_replica_batch.py ../config/config2.json --fail=1

python3 run_client_batch.py ../config/config2.json
```

### 3. Deal with f primary failures
In our config file, we set f = 2, if you want to have higher f,

you need to add more replicas in the config file to have a higher failure tolerance

```
python3 run_replica_batch.py ../config/config2.json --fail=2

python3 run_client_batch.py ../config/config2.json
```

### 4. Skip slot
you need to identify the specific slot you want to skip with option ```--skip=x``` in the command line

Once the old leader skip the slots on purpose, other replicas
will require a view change since they found the old promary is not making any progress.
Then the new leader will detect the hole and fill the skipped slot with "nullop" to
preceed the process

run batch mode
```
python3 run_replica_batch.py ../config/config2.json --skip=x
python3 run_client_batch.py ../config/config2.json
```

### 5. Simulating message loss

our program can be consistent under loss rate no greater than 0.2, for 
lager loss rate, we won't ganarantee consistency

run batch mode
```
python3 run_replica_batch.py ../config/config2.json --p=0.2
python3 run_client_batch.py ../config/config2.json --p=0.2
```
