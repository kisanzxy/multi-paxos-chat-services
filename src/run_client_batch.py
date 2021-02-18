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
from subprocess import call

@click.command()
@click.argument("config", nargs=1, type=click.Path(exists=True))
@click.option('--p', required=False, type=float, default=0)
def main(config, p):
    with open(config, 'r') as f:
        data = f.read()
        f, replicas, clients = parse_config(data)
    # client_list = list()
    # processes = list()
    # messages = ['../config/message1.txt','../config/message2.txt','../config/message3.txt']
    # for client in clients:
    #     c = Client(client.server_id, client.host, client.port, replicas, messages[client.server_id], p)
    #     client_list.append(c)
    # for c in client_list:
    #     process = Process(target = c.run)
    #     process.start()
    #     processes.append(process)
    call(['bash','start_clients.sh', str(len(clients)), config, str(p)])

if __name__ == '__main__':
    main()