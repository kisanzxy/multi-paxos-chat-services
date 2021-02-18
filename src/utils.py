import socket
import time
import random
import logging
import json
import sys

#message types
PREPARE = 'PREP' # I am learder
PROMISE= 'PROM' # you are leader
PROPOSE = 'PROP' # decree
ACCEPT = 'ACPT' # accept from acceptors
VIEWCHANGE = 'VICH' # viewchange message
REPLY = 'ACK' # reply message to client
REQUEST = 'REQ' # request message from client
HEARTBEAT = 'H' # Heartbeat from leader
NULLOP = 'null_op'
QUERY = 'QERY'
RESPOND = 'RESP'

TIMEOUT = 'TOUT'

PROCESS_TIMEOUT = 5

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    stream=sys.stdout
                    )


def send(host, port, msg, loss_rate=0):
    """
    param:  
        s: socket
        host: host addr
        port: port number
        msg: str, message
        loss_rate: float (0, 1)
    """
    if loss_rate > 0:
        if random.uniform(0, 1) < loss_rate:
            return
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # s.connect((host, port))
        s.sendto(json.dumps(msg).encode('utf-8'), (host, port))
        logging.info("SEND: %s to host:%s, port:%s", str(msg), str(host), str(port))
    except socket.error:
            logging.debug("reconnet and resend due to socket error")
            # s.connect((host, port))
            s.sendto(json.dumps(msg).encode('utf-8'), (host, port))
    s.close()
          
def receive(s, handle_msg):
    while True:
        # conn, addr = s.accept()
        # logging.info("CONNECT: %s", str(addr))
        try:
            data = s.recv(4096*2)
        except BlockingIOError:
            # logging.info("ioblocking")
            # time.sleep(1)
            continue
        except socket.timeout:
            # logging.info("timeout, resend")
            continue
        if not data:
            continue
        msg = json.loads(data)
        logging.info('RCVD: %s', str(msg))
        handle_msg(msg) # need to be implemented. 
        # conn.close()


class ConfigModel(object):
    """
    param:
        server_id: unique id, int
        host: host addr
        port: port number
        s: socket
    """
    def __init__(self, server_id, host, port, s=None):
        self.server_id = server_id
        self.host = host
        self.port = port
        self.s = s


def parse_config(config_file):
    data = json.loads(config_file)
    f = data['f']
    clients = []
    for entry in data['clients']:
        config = ConfigModel(entry['id'], entry['host'], entry['port'])
        clients.append(config)
    replicas = []
    for entry in data['replicas']:
        replica = ConfigModel(entry['id'], entry['host'], entry['port'])
        replicas.append(replica)
    return f, replicas, clients

    


