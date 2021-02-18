import socket    
import click  
from multiprocessing import Process
from requests import get
from utils import *
from replica import *
from pathlib import Path
from subprocess import call

@click.command()
@click.argument("config", nargs=1, type=click.Path(exists=True))
@click.option('--p', required=False, type=float, default=0)
@click.option('--skip', required=False, type=int, default=-1)
@click.option('--fail', required=False, type=int, default=-1)
def main(config, p, skip, fail):
    with open(config, 'r') as f:
        data = f.read()
        f, replicas, clients = parse_config(data)
    # replica_list = list()
    # processes = list()
    # for replica in replicas:
    #     log_file_name = Path('../logs/replica_'+str(replica.server_id)+'.txt')
    #     r = Replica(f, replica.server_id, skip, replicas, clients, log_file_name, p)
    #     replica_list.append(r)
    # for r in replica_list:
    #     process = Process(target = r.run)
    #     process.start()
    #     processes.append(process)
    call(['bash','start_servers.sh', str(2*f+1), config, str(p), str(skip), str(fail)])


if __name__ == '__main__':
    main()