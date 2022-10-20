from time import time
import hashlib
from urllib.parse import urlparse
import requests
import json
import random

class Blockchain:
    def __init__(self, port):
        self.port = port
        self.current_transactions = []
        self.chain = []

    def valid_chain(self, chain):
        # Determine if a given blockchain is valid
        # :param chain: A blockchain
        # :return: True if valid, False if not

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        # This is our consensus algorithm, it resolves conflicts
        # by replacing our chain with the longest one in the network.
        # :return: True if our chain was replaced, False if not

        neighbours = self.nodes
        new_chain = None

        # only when a chain is longer than this chain, it will be replaced
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            try:
                response = requests.get(f'http://{node}/api/chain')
                print(node)
                print(response)
                if response.status_code == 200:
                    print(response)
                    length = response.json()['length']
                    chain = response.json()['chain']

                    # Check if the length is longer and the chain is valid
                    if length > max_length and self.valid_chain(chain):
                        max_length = length
                        new_chain = chain
            except:
                continue
        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
        return False


    def already_voted(self, voter_id):
        current_index = 0
        while current_index < len(self.chain):
            transactions_in_block = self.chain[current_index]['transactions']
            for transaction in transactions_in_block:
                if transaction['voter'] == voter_id:
                    return True
            current_index += 1
        return False

    def new_block(self, proof):
        # Create a new Block in the Blockchain
        # :param proof: The proof given by the proof of work algorithm
        # :return: new Block

        previous_hash = ""
        if len(self.chain) != 0:
            previous_hash = self.chain[-1]['previous_hash']
        
        block = {
            'index': len(self.chain),
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash,
        }

        # Reset the current list of transactions
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, voter, voted_for):
        # Creates a new transaction to go into the next mined Block.
        # This will not be mined/verified unless we call the mine function.
        # It will just sit on the local disk
        # :param voter: public key of voter
        # :param voted_for: encrypted choice of voter

        for transaction in self.current_transactions:
            if transaction['voter'] == voter:
                # this voter's vote is already waiting to be mined.
                # therefore, rejected.
                return
        self.current_transactions.append({
            'voter': voter,
            'voted_for': voted_for
        })


    def hash(block):
        # Creates a SHA-256 hash of a block
        # :param block: block
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()   # hashlib.sha256 returns an object

    def proof_of_work(self):
        
        # Proof of Work:
        #  - Find a number nonce such that hash({current_transactions}{proof}{previous_hash}) contains leading 4 zeroes
        # :return: <int> proof of work

        last_hash = ""
        if len(self.chain) != 0:
            last_hash = self.chain[-1]['previous_hash']
        proof = 0
        while self.valid_proof(self.current_transactions, proof, last_hash) is False:
            proof += 1
        return proof


    def valid_proof(self, current_transactions, proof, last_hash):
        # Validates the Proof
        # :param current_transactions: <dict> List of transactions
        # :param proof: <int> Current Proof to test
        # :param last_hash: <str> The hash of the previous block
        # :return: <bool> True if correct, False if not.

        trial = f'{current_transactions}{proof}{last_hash}'.encode()
        trial_hash = hashlib.sha256(trial).hexdigest()
        if trial_hash[:4] == "0000":
            print("Hash found: " + trial_hash)
        return trial_hash[:4] == "0000"