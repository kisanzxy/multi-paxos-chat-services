from utils import *
class Slot:
    def __init__(self, slot_num, f):
        self.slot_num = slot_num
        self.f = f
        self.totla_p = 2*f + 1
        self.majority = f + 1
        self.acc_counter = {}
        self.msg_log = {}

    def addAcceptence(self, msg):
        proposal_id = msg['proposal_id']
        if proposal_id not in self.acc_counter:
            self.acc_counter[proposal_id] = {}
        self.acc_counter[proposal_id][msg['acceptor_id']] = True

        print("For Slot Number", self.slot_num,
            "Proposal ",proposal_id,
            "gets",len(self.acc_counter[proposal_id]),"votes")

        if proposal_id not in self.msg_log:
               self.msg_log[proposal_id] = []
        self.msg_log[proposal_id].append(msg)

    def isAcceptedByMajority(self, proposal_id):
        print("Current vote:", len(self.acc_counter[proposal_id]))
        if len(self.acc_counter[proposal_id]) >= self.majority:
            return True
        return False


class Learner:
    def __init__(self, f, lid, loss_rate=0):
        """
        f: tolerate failure num
        lid: leanrer id
        loss_rate: message loss_rate
        """
        self.f=f                # tolerated failures
        self.total_p=2*f+1      # total process
        self.majority=f+1       # majority process
        self.slots = {}   
        self.decide_log = {}
        self.execute_log = {}
        self.lid = lid      #learner id
        self.loss_rate = loss_rate
        self.next_unexecuted_slot = 0

    def isAcceptedByMajority(self, slot_num, proposal_id):
        if slot_num not in self.slots:
            return False
        return self.slots[slot_num].isAcceptedByMajority(proposal_id)

    def addAcceptance(self, accept_msg):
        """
        after receive a accept msg, add these accept msg to the
        corresponding slot_num.
        """
        slot_to_filled = accept_msg['slot_num']
        proposal_id = accept_msg['proposal_id']
        if slot_to_filled not in self.slots:
            self.slots[slot_to_filled] = Slot(slot_to_filled, self.f)
        self.slots[slot_to_filled].addAcceptence(accept_msg)

    def decide(self, slot_num, proposal_id):
        """
        param:
        slot_num: current slot_num to be decided
        """
        self.slots[slot_num].decide_id = proposal_id
        decide_val= self.slots[slot_num].msg_log[proposal_id][0]['value']
        client_info = self.slots[slot_num].msg_log[proposal_id][0]['client_info']
        self.decide_log[slot_num] = (decide_val, client_info)
        logging.info('learner %s decide slot %s', str(self.lid), str(slot_num))
        # since decided, send reply, as it will eventually happen
        if decide_val != NULLOP:
            msg = {
                'type': REPLY,
                'clseq': client_info['clseq']
            }
            host, port = client_info['host'], client_info['port']
            send(host, port, msg, self.loss_rate)

    def execute(self, log_file):
        # if len(self.execute_log) == 0:
        #     self.next_unexecuted_slot = 0
        # else:
        #     self.next_unexecuted_slot = max(self.execute_log.keys())
        while self.next_unexecuted_slot in self.decide_log:
            self.execute_log[self.next_unexecuted_slot] = self.decide_log[self.next_unexecuted_slot][0]
            logging.info('learner %s learn slot %s as value: %s', str(self.lid), str(self.next_unexecuted_slot), self.execute_log[self.next_unexecuted_slot])
            with open(log_file, 'a') as f:
                f.write(self.execute_log[self.next_unexecuted_slot]+'\n')
            self.next_unexecuted_slot += 1
        
        if self.next_unexecuted_slot < max(self.decide_log.keys()):
            return False
        return True

    def query_others(self, targets, loss_rate):
        """
        query others for a undecided slot
        """
        msg = {'type': QUERY, 'slot_num': self.next_unexecuted_slot, 'lid': self.lid}
        for target in targets:
            send(target.host, target.port, msg)


    def learn(self, learn_msg, log_file):
        # others tell me about my missing slot
        learned_slot = learn_msg['slot_num']
        learned_value = learn_msg['value']
        learned_client_info = learn_msg['client_info']
        self.decide_log[learned_slot] = (learned_value, learned_client_info)
        return self.execute(log_file)


    def process_accept(self, accept_msg):
        self.addAcceptance(accept_msg)
        if self.isAcceptedByMajority(accept_msg['slot_num'], accept_msg['proposal_id']):
            # print("Slot", accept_msg['slot_num'], 
            #       "proposal", accept_msg['proposal_id'], "is majority")
            return True
        else:
            return False
        
    def process_query(self, query_msg, targets, loss_rate):
        queried_slot = query_msg['slot_num']
        querier_id = query_msg['lid']
        if queried_slot in self.decide_log:
            reply_msg={
                'type' : RESPOND,
                'slot_num' : queried_slot,
                'value' : self.decide_log[queried_slot][0],
                'client_info' : self.decide_log[queried_slot][1]
            }
            # print("I know the query, sending:", reply_msg)
            send(targets[querier_id].host, targets[querier_id].port, reply_msg)
            return True
        else:
            return False