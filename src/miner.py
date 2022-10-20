import socket
import json
import random
import hashlib
from blockchain import Blockchain

voters = ['']
candidates = ['0', '1', '2', '3', '4']
MAX_TRANSACTIONS = 2

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

host = socket.gethostname()
port = 29170

g = 961
p = 997

sock.bind((host, port))

blockchain = Blockchain(port)

def processTransactions():
    if len(blockchain.current_transactions) == MAX_TRANSACTIONS:
        return
    data, addr = sock.recvfrom(1024)
    data = json.loads(data.decode('utf-8'))
    data = data

    # Make sure that the voter hasn't already voted
    if blockchain.already_voted(data['voter']):
        return

    fail = 0

    # Run the ZKP proof for 5 rounds
    for i in range(1, 6): 

        if fail:
            break

        msg = "Round " + str(i) + " inititated..."
        print(msg)
        sock.sendto(msg.encode('utf-8'), addr)

        yh, addr = sock.recvfrom(1024)
        yh = yh.decode('utf-8')
        yh = yh.split(' ')
        y = int(yh[0])
        h = int(yh[1])

        b = random.randint(0, 1)
        sock.sendto(str(b).encode('utf-8'), addr)

        s, addr = sock.recvfrom(1024)
        s = s.decode('utf-8')
        s = int(s)

        if pow(g, s, p) != (h*pow(y,b,p))%p:
            # print(pow(g, s, p), pow(h, y, p))
            fail = 1
            msg = "Failed"
            print("Zero knowledge proof verification failed")
            sock.sendto(msg.encode('utf-8'), addr)

    if fail:
        return

    # Voter is verfied
    msg = "Voter has been verified"
    sock.sendto(msg.encode('utf-8'), addr)
    print(msg)

    # Add the transaction(vote) to the current block
    blockchain.new_transaction(data['voter'], data['voted_for'])


# Main process for the miner
def mineBlock():

    genesis_block_proof = blockchain.proof_of_work()
    blockchain.new_block(genesis_block_proof)

    print('Genesis Block created')
    print('Index: ', blockchain.chain[-1]['index'])
    print('Timestamp: ', blockchain.chain[-1]['timestamp'])
    print('Transactions: ', blockchain.chain[-1]['transactions'])
    print('Proof: ', blockchain.chain[-1]['proof'])

    while True:

        while len(blockchain.current_transactions) < MAX_TRANSACTIONS:
            processTransactions()

        proof = blockchain.proof_of_work()

        blockchain.new_block(proof)

        print('Added New Block')
        print('Index: ', blockchain.chain[-1]['index'])
        print('Timestamp: ', blockchain.chain[-1]['timestamp'])
        print('Transactions: ', blockchain.chain[-1]['transactions'])
        print('Proof: ', blockchain.chain[-1]['proof'])

mineBlock()