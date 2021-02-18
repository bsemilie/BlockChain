import atexit
import json
import os

import sys
from functools import partial

from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Qt, Slot, Signal, QObject

import threading
import zmq

#  files imports
from chain import Blockchain
from key import BitcoinAccount

# wallet generation

wallet = BitcoinAccount()
address = wallet.to_address()
file_name = "wallets/" + address + ".json"
wallet.to_file(file_name)

#  blockchain data

difficulty = 3
blockchain = None
peers = set()

# list_ports = ["5556", "5557", "5558"]

port_bind = "5000"
if len(sys.argv) > 1:
    port_bind = sys.argv[1]

context = zmq.Context()
socket = context.socket(zmq.PUB)

socket.bind("tcp://*:%s" % port_bind)

topic = ""
ip = "localhost" + ":" + port_bind
socket_sub = context.socket(zmq.SUB)
for elem in list(peers):
    if elem != ip:
        socket_sub.connect("tcp://%s" % elem)
socket_sub.setsockopt_string(zmq.SUBSCRIBE, topic)


class Connection(QObject):
    write_block = Signal(str)


ConnectionWrite = Connection()


def reading_network():
    global blockchain
    global ConnectionWrite
    while True:
        [topic_val, msg_val] = socket_sub.recv_multipart()
        topic = topic_val.decode()
        chain_data = json.loads(msg_val.decode())
        if(topic == "chain"):
            if(blockchain and len(blockchain.chain) < chain_data["length"]) or blockchain is None:
                blockchain = Blockchain(difficulty, chain_data["chain"])
                ConnectionWrite.write_block.emit(str(blockchain.chain[-1]))



class Chain_Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chain")

        chain_layout = QtWidgets.QFormLayout()

        chain_label = QtWidgets.QLabel(
            json.dumps(blockchain.to_dict(), indent=4, sort_keys=True)
        )
        chain_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidget(chain_label)
        self.scrollArea.setWidgetResizable(True)

        chain_layout.addWidget(self.scrollArea)
        self.setLayout(chain_layout)


class Tx_Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Send Transaction")

        self.buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        self.buttonBox.accepted.connect(self.working_click)
        self.buttonBox.rejected.connect(self.reject)

        tx_layout = QtWidgets.QFormLayout()

        self.tx_address = QtWidgets.QLineEdit()

        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        self.tx_address.textChanged.connect(self.allowButton)

        self.tx_amount = QtWidgets.QSpinBox()
        self.tx_amount.setRange(0, 999999999)
        # self.tx_amount.setValue(0)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        tx_layout.addRow("Adress of receiver: ", self.tx_address)
        tx_layout.addRow("Amount to send: ", self.tx_amount)
        tx_layout.addWidget(self.buttonBox)
        self.setLayout(tx_layout)

    def allowButton(self):
        if len(self.tx_address.text()) > 0:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(
                True
            )
        elif self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).isEnabled():
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(
                False
            )

    def get_values(self):
        if self.tx_address and self.tx_amount:
            return {
                "address": self.tx_address.text(),
                "amount": int(self.tx_amount.text()),
            }
        else:
            return False

    def working_click(self):
        pending_transaction = self.get_values()
        blockchain.add_transaction(address, pending_transaction["address"], pending_transaction["amount"])
        self.accept()


class Peer_Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add peer")

        self.buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        self.buttonBox.accepted.connect(self.working_click)
        self.buttonBox.rejected.connect(self.reject)

        tx_layout = QtWidgets.QFormLayout()

        self.peer_address = QtWidgets.QLineEdit()

        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        self.peer_address.textChanged.connect(self.allowButton)

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        tx_layout.addRow("Adress of receiver: ", self.peer_address)

        tx_layout.addWidget(self.buttonBox)
        self.setLayout(tx_layout)

    def allowButton(self):
        if len(self.peer_address.text()) > 0:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(
                True
            )
        elif self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).isEnabled():
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(
                False
            )

    def get_peer(self):
        return self.peer_address.text()

    def working_click(self):
        peers.add(self.get_peer())
        self.accept()


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        global ConnectionWrite

        self.text_address = QtWidgets.QLabel("My address: ")
        self.address_value = QtWidgets.QLabel(address)
        self.address_value.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse
        )
        self.text_ip = QtWidgets.QLabel("My IP: ")
        self.ip_value = QtWidgets.QLabel(ip)
        self.ip_value.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.button_tx = QtWidgets.QPushButton("Send transaction")
        self.button_chain = QtWidgets.QPushButton("Chain")
        self.button_mine = QtWidgets.QPushButton("Mine")
        self.button_peer = QtWidgets.QPushButton("Add peer")

        self.text_peerlist = QtWidgets.QLabel("Peers: ")

        self.text_pending = QtWidgets.QLabel("Pending tx: ")

        self.text_block = QtWidgets.QLabel("Last block: ")

        self.layout = QtWidgets.QVBoxLayout()

        # layout for the address
        layout_address = QtWidgets.QHBoxLayout()
        layout_address.addWidget(self.text_address)
        layout_address.addWidget(self.address_value)
        self.layout.addLayout(layout_address)

        # layout for the ip
        layout_ip = QtWidgets.QHBoxLayout()
        layout_ip.addWidget(self.text_ip)
        layout_ip.addWidget(self.ip_value)
        self.layout.addLayout(layout_ip)

        # layout for the buttons

        layout_buttons = QtWidgets.QHBoxLayout()
        layout_buttons.addWidget(self.button_tx)
        layout_buttons.addWidget(self.button_chain)
        layout_buttons.addWidget(self.button_mine)
        layout_buttons.addWidget(self.button_peer)
        self.layout.addLayout(layout_buttons)

        self.layout.addWidget(self.text_peerlist)
        self.peers_layout = QtWidgets.QFormLayout()
        self.tx_layout = QtWidgets.QFormLayout()
        self.block_data = QtWidgets.QLabel()
        self.block_data.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse
        )

        self.layout.addLayout(self.peers_layout)
        self.layout.addWidget(self.text_pending)
        self.layout.addLayout(self.tx_layout)
        self.layout.addWidget(self.text_block)
        self.layout.addWidget(self.block_data)

        self.setLayout(self.layout)

        self.button_tx.clicked.connect(self.send_tx)
        self.button_chain.clicked.connect(self.print_chain)
        self.button_mine.clicked.connect(self.mine_call)
        self.button_peer.clicked.connect(self.add_peer)

        ConnectionWrite.write_block.connect(self.get_block_str)

    def print_chain(self):
        if blockchain:
            chain_window = Chain_Dialog()
            chain_window.exec_()

        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText(
                "No chain: you need to mine the first block or get the chain "
                "from another peer before seeing the chain"
            )
            msg.setWindowTitle("No blockchain")

            msg.exec_()

    def mine_call(self):
        global blockchain
        if not blockchain:
            blockchain = Blockchain(difficulty)
            blockchain.create_genesis_block()
        else:
            blockchain.mine_block()

        self.define_block(blockchain.chain[-1])
        chain = blockchain.to_dict()
        chain_data = json.dumps({"length": len(chain), "chain": chain}).encode()

        socket.send_multipart([b'chain',chain_data])

    @Slot(str)
    def get_block_str(self, block_str):
        self.block_data.setText(block_str)

    def define_block(self, block):
        self.block_data.setText(str(block))
        for row in range(self.tx_layout.rowCount()):
            self.tx_layout.removeRow(0)

    def send_tx(self):
        global blockchain
        # open the tx dialog window
        if blockchain:
            tx_window = Tx_Dialog()
            ret_val = tx_window.exec_()
            if ret_val == 1 and blockchain is not None:
                tx_data = tx_window.get_values()
                self.define_tx(tx_data)

        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText(
                "No chain: you need to mine the first block or get the chain "
                "from another peer before sending transactions"
            )
            msg.setWindowTitle("No blockchain")

            msg.exec_()

    def define_tx(self, elem):
        text = (
            "Tx: { address : "
            + elem["address"]
            + ", amount : "
            + str(elem["amount"])
            + " }"
        )
        text_tx = QtWidgets.QLabel(text)
        text_tx.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.tx_layout.addRow(text_tx)

    def define_peer(self, elem):
        text_peer = QtWidgets.QLabel(elem)
        text_peer.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        button_peer = QtWidgets.QPushButton("X")
        button_peer.setFixedSize(20, 20)
        button_peer.clicked.connect(
            partial(self.remove_peer, elem, text_peer, button_peer)
        )
        self.peers_layout.addRow(text_peer, button_peer)

    def add_peer(self):
        global ip
        peer_window = Peer_Dialog()
        ret_val = peer_window.exec_()
        if ret_val == 1:
            peer_address = peer_window.get_peer()
            if peer_address != ip:
                peers.add(peer_address)
                socket_sub.connect("tcp://%s" % peer_address)
                self.define_peer(peer_address)

    def remove_peer(self, elem, text_peer, button_peer):
        peers.remove(elem)
        socket_sub.disconnect("tcp://%s" % elem)

        button_peer.deleteLater()
        text_peer.deleteLater()


def clean_file():
    os.remove(file_name)


atexit.register(clean_file)

if __name__ == "__main__":
    t = threading.Thread(target=reading_network)
    t.daemon = True  #  to close when main loop close
    t.start()

    app = QtWidgets.QApplication([])

    widget = MyWidget()

    scrollArea = QtWidgets.QScrollArea()

    scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    scrollArea.setWidgetResizable(True)

    scrollArea.setWidget(widget)
    scrollArea.resize(800, 600)
    scrollArea.setWindowTitle("Blockchain")
    scrollArea.show()

    sys.exit(app.exec_())
