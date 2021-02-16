import time
import copy
from block import Block
from transaction import Transaction


class Blockchain:
    def __init__(self, difficulty):
        self.chain = []
        self.difficulty = difficulty
        self.transactions_pool = []
        
        
    @property
    def last_block(self):
        return self.chain[-1]

    def create_genesis_block(self):
        genesis_block = Block(0,"")
        genesis_block.hashval = genesis_block.hash_func()
        self.chain.append(genesis_block)
        
    
    def add_transaction(self, sender, receiver, amount):
        transaction = Transaction(sender, receiver, amount)
        self.transactions_pool.append(transaction)
        
        
    def add_block(self, block):
        previous_hash = self.last_block.hashval
        if previous_hash != block.last_hash:
            return False
        if not block.verify():
            return False
        self.chain.append(block)
        
        
    def mine_block(self):
        if not self.transactions_pool:
            return False
        last_block = self.last_block
        new_block = Block(last_block.blockNumber + 1, last_block.hashval)
        for elem in self.transactions_pool:
            new_block.add_transaction(elem)
        
        new_block.mine(self.difficulty)
    
        self.add_block(new_block)
        self.transactions_pool = []
        return new_block.blockNumber
        
    
    def verify_chain():
        pass
    
    def to_dict(self):
        chain_dict = []

        for elem in self.chain:

            chain_dict.append(elem.to_dict())

      
        return chain_dict