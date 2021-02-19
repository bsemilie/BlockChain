import hashlib
import time
from transaction import Transaction
from key import verify_signature, Account


class Block:
    def __init__(self, blockNumber, last_hash, nonce=0, timestamp=0, transactions=[],hash= None, minerName=None, signature= None):
        self.transactions = []
        for elem in transactions:
            self.transactions.append(Transaction(elem["sender"], elem["receiver"], elem["amount"], elem["timestamp"], elem["tx_number"], elem["signature"]))

        self.timestamp = timestamp
        self.blockNumber = blockNumber
        self.last_hash = last_hash
        self.hashval = hash
        self.Nonce = nonce
        self.minerName = minerName
        self.signature = {
        bytes.fromhex(signature) if signature is not None else signature
        }


    def add_transaction(self,transaction: Transaction):
        tx = transaction
        tx.tx_number = len(self.transactions)
        self.transactions.append(tx)

    def hash_func(self):
        sha = hashlib.sha256()
        data =""
        data = str(self.blockNumber) + str(self.Nonce) + str(self.last_hash)
        for transaction in self.transactions:
            data += str(transaction.sender) + str(transaction.receiver) + str(transaction.amount)

        sha.update(data.encode())

        return sha.hexdigest()

    def verify(self):
        computed_hash = self.hash_func()
        if computed_hash != self.hashval:
            return False
        return True


    def mine(self, difficulty, account):
        self.timestamp = time.time()
        prefix = "0" * difficulty
        h = self.hash_func()
        while(h.startswith(prefix) == False):
             self.Nonce +=1
             h = self.hash_func()

        self.hashval = h
        self.minerName = account.to_address()
        self.sign_block(account)







    def __repr__(self):

        string = "Block number: " + str(self.blockNumber) + "\n" + \
            "Timestamp: " + str(self.timestamp) + "\n" + \
                "Nonce: " + str(self.Nonce) + "\n" + \
                    "Previous hash: " + str(self.last_hash) + "\n" + \
                        "Hash: " + str(self.hashval) + "\n" + \
                            "Miner: " + str(self.minerName) + "\n"
        if self.signature is not None:
            str_sign = "Signature: " + str(self.signature.hex())
            string += str_sign
        return string


    def to_dict(self):

        block_dict = {}
        block_dict["Block number"] = self.blockNumber

        block_dict["nonce"] = self.Nonce

        block_dict["timestamp"] = self.timestamp

        block_dict["miner"] = self.minerName

        block_dict["transactions"] = []

        for elem in self.transactions:

            block_dict["transactions"].append(elem.to_dict())

        block_dict["Last hash"] = self.last_hash

        block_dict["hashval"] = self.hashval

        if self.signature is not None:
            block_dict["signature"] = self.signature.hex()
        else:
            block_dict["signature"] = self.signature


        return block_dict

    def sign_block(self, account):
        string = "Block number: " + str(self.blockNumber) + "\n" + \
            "Timestamp: " + str(self.timestamp) + "\n" + \
                "Nonce: " + str(self.Nonce) + "\n" + \
                    "Previous hash: " + str(self.last_hash) + "\n" + \
                        "Hash: " + str(self.hashval) + "\n" + \
                            "Miner: " + str(self.minerName) + "\n"
        self.signature = account.sign(string);

    def verify_block(self):
        string = "Block number: " + str(self.blockNumber) + "\n" + \
            "Timestamp: " + str(self.timestamp) + "\n" + \
                "Nonce: " + str(self.Nonce) + "\n" + \
                    "Previous hash: " + str(self.last_hash) + "\n" + \
                        "Hash: " + str(self.hashval) + "\n" + \
                            "Miner: " + str(self.minerName) + "\n"
        if verify_signature(self.signature.hex(), string, self.minerName)!= True:
            return False
        for elem in self.transactions:
            if elem.verify_tx() != True:
                return False
        computed_hash = self.hash()
        if(computed_hash != self.hashval):
            return False
        return True
