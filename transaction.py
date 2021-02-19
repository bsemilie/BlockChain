from key import verify_signature, Account

class Transaction:
    def __init__(self, sender, receiver, amount, time=0, tx_number=None, signature=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.time = time
        self.tx_number = tx_number
        self.signature = {
        bytes.fromhex(signature) if signature is not None else signature
        }

    def __repr__(self):

        string = "Transaction number: " + str(self.tx_number) + "\n" + \
                 "Sender: " + str(self.sender) + "\n" + \
                 "Receiver: " + str(self.receiver) + "\n" + \
                 "Amount: " + str(self.amount) + "\n" + \
                 "Timestamp: " + str(self.time) + "\n"
        if self.signature is not None:
            str_sign = "Signature: " + str(self.signature.hex())
            string += str_sign

        return string

    def to_dict(self):

        tx_dict = {}

        tx_dict["tx_number"] = self.tx_number

        tx_dict["sender"] = self.sender

        tx_dict["receiver"] = self.receiver

        tx_dict["amount"] = self.amount

        tx_dict["timestamp"] = self.time

        if self.signature is not None:
            tx_dict["signature"] = self.signature.hex()
        else:
            tx_dict["signature"] = self.signature


        return tx_dict

    def sign_tx(self,account):

        string = "Transaction number: " + str(self.tx_number) + "\n" + \
                 "Sender: " + str(self.sender) + "\n" + \
                 "Receiver: " + str(self.receiver) + "\n" + \
                 "Amount: " + str(self.amount) + "\n" + \
                 "Timestamp: " + str(self.time) + "\n"
        self.signature  = account.sign(string);

    def verify_tx(self):
        string = "Transaction number: " + str(self.tx_number) + "\n" + \
                 "Sender: " + str(self.sender) + "\n" + \
                 "Receiver: " + str(self.receiver) + "\n" + \
                 "Amount: " + str(self.amount) + "\n" + \
                 "Timestamp: " + str(self.time) + "\n"
        return verify_signature(self.signature.hex(), string, self.sender)
