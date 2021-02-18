import time
from block import Block
from transaction import Transaction


class Blockchain:
    def __init__(self, difficulty, chain=[], block_reward=50):
        self.chain = []
        for elem in chain:
            newBlock = Block(elem["Block number"], elem["Last hash"], elem["nonce"], elem["timestamp"], elem["transactions"], elem["hashval"], elem["miner"])
            self.chain.append(newBlock)
        self.difficulty = difficulty
        self.transactions_pool = []
        self.block_reward = block_reward


    @property
    def last_block(self):
        return self.chain[-1]

    def create_genesis_block(self):
        genesis_block = Block(0,"")

        new_tx = Transaction("network", "me", self.block_reward, time.time() )
        genesis_block.add_transaction(new_tx)
        nonce = genesis_block.mine(self.difficulty)
        self.chain.append(genesis_block)


    def add_transaction(self, sender, receiver, amount):
        transaction = Transaction(sender, receiver, amount, time.time())
        self.transactions_pool.append(transaction)


    def add_block(self, block):
        if block.timestamp < self.last_block.timestamp:
            print("Timestamp received"+str(block.timestamp))

            print("Timestamp last block"+str(self.last_block.timestamp))

            raise ValueError("Error timestamp is before timestamp of last block")
        if(block.blockNumber != self.last_block.blockNumber+1):

            print("index received"+str(block.blockNumber))

            print("index expected"+str(self.last_block.blockNumber+1))

            raise ValueError("Error in indexing")
        previous_hash = self.last_block.hashval
        if previous_hash != block.last_hash:
            print("Previous hash received"+str(block.last_hash))

            print("Previous hash expected"+str(self.last_block.hashval))

            raise ValueError("block not aligned in the chain")

        if not block.verify():
            print("ERROR: block not valid")

        self.chain.append(block)


    def mine_block(self):
        if not self.transactions_pool:
            print("ERROR: no transactions waiting")
        last_block = self.last_block
        new_block = Block(last_block.blockNumber + 1, last_block.hashval)
        for elem in self.transactions_pool:
            new_block.add_transaction(elem)

        self.transactions_pool.clear()

        new_tx = Transaction("network", "me", self.block_reward, time.time())
        new_block.add_transaction(new_tx)
        nonce = new_block.mine(self.difficulty)

        self.add_block(new_block)



    def verify_chain(self):
        for elem in self.chain:
            if(elem.verify() == False):
                return False

    def to_dict(self):
        chain_dict = []

        for elem in self.chain:

            chain_dict.append(elem.to_dict())


        return chain_dict
