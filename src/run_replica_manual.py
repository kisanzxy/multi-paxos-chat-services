import socket    
import select
import threading
import sys
import time
import logging
import click  
from multiprocessing import Process
from requests import get
from utils import *
from replica import *
from pathlib import Path

@click.command()
@click.argument("config", nargs=1, type=click.Path(exists=True))
@click.option('--rid', required=True, type=int)
@click.option('--p', required=False, type=float, default=0)
@click.option('--skip', required=False, type=int, default=-1)
@click.option('--fail', required=False, type=int, default=-1)
def main(config, rid, p, skip, fail):
    print("Starting server", rid)
    with open(config, 'r') as f:
        data = f.read()
        f, replicas, clients = parse_config(data)

    log_file_name = Path('../logs/replica_'+str(rid)+'.txt')
    r = Replica(f, rid, skip, fail, replicas, clients, log_file_name, p)
    print("Created server", rid)
    r.run()
        

if __name__ == '__main__':
    main()