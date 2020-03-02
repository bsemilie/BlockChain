from chain import Blockchain
from key import BitcoinAccount

wallet = BitcoinAccount()
address = wallet.to_address()
difficulty = 4

blockchain =  Blockchain(difficulty)
blockchain.create_genesis_block(wallet)

print("blockchain: ")
print(blockchain.to_dict())

first_block = blockchain.chain[-1]

print("First block: ")
print(first_block)

blockchain.add_transaction(address,"colas", 10,wallet)
blockchain.add_transaction(address,"salim", 30,wallet)
blockchain.mine_block(wallet)

print("blockchain: ")
print(blockchain.to_dict())
second_block = blockchain.chain[-1]

print("Second block: ")
print(second_block)

