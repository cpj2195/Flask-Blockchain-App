import datetime
import hashlib
import json
import requests
from uuid import uuid4
from urlparse import urlparse


class Block:
    def __init__(self,data):
        self.data = data
        self.prev = None
        self.next = None


class BlockChain:
    def __init__(self):
        self.head = None
        self.transactions = []
        self.insertBlock(proof=1,prev_hash='0')
        self.nodes = set()
    

    def insertBlock(self, prev_hash,proof):
        if(prev_hash is None):
            print("Plese enter a previous hash ")
            return
        elif (proof is None):
            print("Please enter a proof for your Block")
            return
        
        else:
            new_data = {"timestamp":str(datetime.datetime.now()),'proof': proof, "prev_hash":prev_hash, "transactions":  self.transactions}
            new_block = Block(new_data)
            test_node = self.head
            if(self.head is None):
                self.head = new_block
                new_block.next = None
                return
            while(test_node.next is not None):
                test_node = test_node.next

            if(test_node is None):
                print("No Node with the previous hash is there")
            else:
                new_block.next = None
                test_node.next = new_block
                new_block.prev = test_node
                return new_block


    def insert_infront(self,new_data):
        if(new_data.get('prev_hash') is None):
            print("Your data does not have a previous Hash")
            return
        else:
            new_block = Block(new_data)
            new_block.next = self.head
            if self.head is not None: 
                self.head.prev = new_block
            
            self.head = new_block
    
    def insert_atend(self,new_data):
        if(new_data.get('prev_hash') is None):
            print("Your data does not have a previous Hash")
            return
        else:
            new_block = Block(new_data)
            if self.head is None:
                self.head = new_block
                new_block.next = None
                new_block.prev = None
                return
            else:
                test_node = self.head
                while(test_node.next is not None):
                    test_node = test_node.next
                test_node.next = new_block
                new_block.prev = test_node
                new_block.next = None
        
    
    def get_length(self):
        if self.head is None:
            return 0
        else: 
            count = 0 
            test_node = self.head
            while(test_node is not None):
                count = count+1
                test_node = test_node.next
        return count
    
    def printList(self):
        if(self.head is None):
            return
        else:
            test_node = self.head
            while(test_node is not None):
                print(test_node.data)
                test_node = test_node.next
    
    def get_last_block(self):
        if(self.head is None):
            return
        else:
            test_node = self.head
            while(test_node.next is not None): 
                test_node = test_node.next
        return test_node
    
    def proof_of_work(self,previous_proof):
        check_proof = False
        new_proof = 1
        while(not check_proof):
            hash_op = hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if(hash_op[:4]=='0000'):
                check_proof = True
            else:
                new_proof+=1
        return new_proof

    def hash_block(self,block):
        json_block = json.dumps(block.data,sort_keys = True).encode()
        return hashlib.sha256(json_block).hexdigest()

    def check_chain(self):
        previous_node = self.head
        if(previous_node is None):
            print("The Blockchain is empty")
            return
        else:
            current_block = previous_node.next
            if(current_block is None):
                return
            block_index = 1
            while(previous_node is not None):
                if(current_block.get("prev_hash") != self.hash_block(previous_node)):
                    return False
                prev_proof = previous_node.get("proof")
                current_proof = current_block.get("proof")
                hash_op = hashlib.sha256(str(current_proof**2 - prev_proof**2).encode()).hexdigest()
                if(hash_op[:4]!= '0000'):
                    return False
                previous_node = previous_node.next
            return True
    
    def add_transaction(self,sender,receiver,amount):
        self.transactions.append({"sender":sender,"receiver":receiver,"amount":amount})
        chain_length = self.get_length()
        return chain_length +1
    
    def add_node(self,node_address):
        parsed_url = urlparse(node_address)
        self.nodes.add(parsed_url.netloc)
    

     
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_chain_length = self.get_length()
        new_blockchain = BlockChain()
        for node in network:
            response = requests.get("http://{node}/get_chain".format(node))
            if response.status_code == 200:
                current_length = response.json().get("chain_length")
                current_chain = response.json().get("chain")
                if current_length > max_chain_length:
                    max_chain_length  = current_length
                    longest_chain = current_chain
                    for block in longest_chain:
                        new_blockchain.insert_atend(block)
        if longest_chain is not None:
            self.head = new_blockchain.head
            return True
        return False

