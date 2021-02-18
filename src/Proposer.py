import socket
from utils import *

class Proposer:
    def __init__(self, f, proposer_id, skip):
        """
        param:
            f: tolerate failures num
            proposer_id: replica id
        """
        self.f=f                # tolerated failures
        self.total_p = 2*f+1      # total process
        self.majority = f+1       # majority process
        self.proposal_id = 0        # current proposal number, increasing
        self.proposer_id = proposer_id
        self.skip = skip
        self.slot_num = 0         # next slot number for new request
        self.acc_counter = {}     # acceptance counter
        self.msg_log = {}
        self.need_prepare = True
        self.proposal_log = {}      #used to store what value has been proposed for which slot

    def prepare(self, proposal_id, targets, loss_rate):
        """
        send out I am leader message
        """
        self.proposal_id = proposal_id
        msg = {'type': PREPARE, 'proposal_id': proposal_id, 'proposer_id': self.proposer_id}
        for target in targets:
            send(target.host, target.port, msg, loss_rate)

    def addAcceptence(self, msg):
        """
        add accept for current proposal_id
        """
        proposal_id = msg['proposal_id']
        if proposal_id != self.proposal_id:
            return
        acceptor_id = msg['acceptor_id']
        if proposal_id not in self.acc_counter:
            self.acc_counter[proposal_id] = {}
        # set accept of acceptor_id True
        self.acc_counter[proposal_id][acceptor_id] = True
        if proposal_id not in self.msg_log:
            self.msg_log[proposal_id] = []
        self.msg_log[proposal_id].append(msg)

    def getProposalList(self):
        """
        param:
            decide_log: learner.decide_log
        return a proposal list for new leader
        fill in NULLOP is the slot is empty
        """
        accepted_msgs = self.msg_log[self.proposal_id]
        max_accepted_id = {}    # max accepted proposal id for each slot
        slot_value = {}     # accepted value regarding max accepted proposal id for each slot
        acceptd_client_info = {}
        proposal_list = {}
        for m in accepted_msgs:
            for slot_idx, accepted_id in m['accepted_id'].items():
                slot_idx = int(slot_idx)
                if slot_idx not in max_accepted_id or int(accepted_id) > int(max_accepted_id[slot_idx]):
                    max_accepted_id[slot_idx] = int(accepted_id)
                    slot_value[slot_idx] = m['accepted_value'][str(slot_idx)]
                    acceptd_client_info[slot_idx] = m['accepted_client_info'][str(slot_idx)]

        print("I'm new leader, prepared:")
        print("Max accepted id:", max_accepted_id)
        print("Value:", slot_value)
        print("Client info:", acceptd_client_info)

        # figure out next slot to fill
        last_accepted_slot = 0, 0
        if len(max_accepted_id) == 0:
            last_accepted_slot = -1
        else:
            last_accepted_slot = int(max(max_accepted_id.keys()))

        self.slot_num = last_accepted_slot + 1
        for slot_idx in range(0, self.slot_num):
            if slot_idx in max_accepted_id:
                proposal_list[slot_idx] = {'value': slot_value[slot_idx], 'client_info': acceptd_client_info[slot_idx]}
            else:
                # empty slot due to skip or message drop
                proposal_list[slot_idx] = {'value': NULLOP, 'client_info': None}
        return proposal_list

    def isAcceptedByQuorum(self):
        if self.proposal_id in self.acc_counter and len(self.acc_counter[self.proposal_id]) >= self.majority:
            return True
        return False

    def propose(self, slot_num, request_msg, targets, loss_rate):
        """
        send proposal to all acceptors
        """
        client_info = request_msg['client_info']
        msg = {
            'type': PROPOSE,
            'slot_num': slot_num,
            'proposal_id': self.proposal_id,
            'value': request_msg['value'],
            'client_info': client_info
            }
        if request_msg['value'] != NULLOP:
            client_id, client_req_id = client_info['clseq'][0], client_info['clseq'][1]
            client_seq_num = (client_id, client_req_id)
            self.proposal_log[client_seq_num] = msg
        print("Proposing:", msg)
        for target in targets:
            print("TO: ", target.host, target.port)
            send(target.host, target.port, msg, loss_rate)


    def isNewRequest(self, client_seq_num):
        if client_seq_num in self.proposal_log:
            return False
        return True

    def propose_request(self, msg, targets, loss_rate):

        if msg['value'] == NULLOP:
            self.propose(self.slot_num, msg, targets, loss_rate)
            self.slot_num+=1
        else:
            client_seq_num = (msg['client_info']['clseq'][0],
                            msg['client_info']['clseq'][1])
            print(client_seq_num)
            if self.isNewRequest(client_seq_num):
                print("This is a new request")
                if self.slot_num == self.skip:
                    self.slot_num += 1
                self.propose(self.slot_num, msg, targets, loss_rate)
                self.slot_num += 1
            else:
                # resend the proposed value
                print("This is an old request")
                proposed_msg = self.proposal_log[client_seq_num]
                for target in targets:
                    send(target.host, target.port, proposed_msg, loss_rate)
        

            



