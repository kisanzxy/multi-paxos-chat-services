from utils import *
class Acceptor:        
    def __init__(self, aid, view):
        """
        param:
            aid: acceptor id
            view: current view_number
        """
        self.prev_proposal_id = None
        self.prev_accept_val = None
        self.current_proposal_id = view     # current view
        self.aid = aid     # acceptor id same as replica id
        self.current_proposer_id = 0    # proposer id, same as the leader replica id
        self.accepted_proposal_id = {}
        self.accepted_proposal_value = {}
        self.accepted_client_info = {}

    def process_proposal(self, decree_msg, targets, loss_rate):
        proposal_id = decree_msg['proposal_id']     # same as view number
        if proposal_id < self.current_proposal_id:   # if from a lower view, jsut ignore
            return
        # accept proposal
        slot_num = decree_msg['slot_num']
        value = decree_msg['value']
        client_info = decree_msg['client_info']

        self.accepted_proposal_id[slot_num] = proposal_id
        self.accepted_proposal_value[slot_num] = value
        self.accepted_client_info[slot_num] = client_info

        accept_msg = {
            "type": ACCEPT,
            'proposal_id': proposal_id,
            'acceptor_id': self.aid,
            'slot_num': slot_num,
            'value': value,
            'client_info': client_info
        }
        
        print("Accepting:", accept_msg)
        # send out accept msg to all learners
        for target in targets:
            print("TO:", target.host, target.port)
            send(target.host, target.port, accept_msg, loss_rate)
    
    def promise(self, leader_change_msg, targets, loss_rate):
        proposal_id = leader_change_msg['proposal_id']
        proposer_id = leader_change_msg['proposer_id']
        if proposal_id < self.current_proposal_id:
            return
        self.current_proposal_id = proposal_id
        self.current_proposer_id = proposer_id
        
        print("Promising viewchange with:")
        print("Accepted id", self.accepted_proposal_id)
        print("Accepted value", self.accepted_proposal_value)
        print("Accepted client", self.accepted_client_info)

        # send youaretheleader msg to new leader
        host, port = targets[proposer_id].host, targets[proposer_id].port
        msg = {
            'type': PROMISE,
            'accepted_id': self.accepted_proposal_id,
            'accepted_value': self.accepted_proposal_value,
            'accepted_client_info': self.accepted_client_info,
            'proposal_id': proposal_id,
            'acceptor_id': self.aid,
        }
        send(host, port, msg, loss_rate)
