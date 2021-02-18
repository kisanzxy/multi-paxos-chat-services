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
from client import *
from pathlib import Path

@click.command()
@click.argument("config", nargs=1, type=click.Path(exists=True))
@click.option('--cid', required=True, type=int)
@click.option('--p', required=False, type=float, default=0)
@click.option('--m', required=False, type=int, default=0)
def main(config, cid, p, m):
    print("Starting client", cid)
    with open(config, 'r') as f:
        data = f.read()
        f, replicas, clients = parse_config(data)
        
    messages = [Path('../config/message1.txt'),
                Path('../config/message2.txt'),
                Path('../config/message3.txt')]
    message = messages[m]
    client = clients[cid]
    c = Client(cid, client.host, client.port, replicas, message, p)
    print("Created client", cid)
    c.run()

if __name__ == '__main__':
    main()