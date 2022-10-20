import socket
import json
import hashlib
import random

nodes = [29170]
trustedParty = 29171

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
g = 961
p = 997

def viewUser(voter, voted_for_encrypted):
    print("Voter: ", voter)
    print("Voter choice: ", voted_for_encrypted)

def castVote():
    for node in nodes:
        # Create socket
        host = socket.gethostname()
        port = node

        # Create msg
        voter = input('Enter ID: ')
        voted_for = int(input('Enter candidate choice [0, 1, 2, 3, 4]: '))
        voted_for_encrypted = hashlib.sha256(str(voted_for).encode('utf-8')).hexdigest()


        # Send to node
        msg = {'voter': voter, 'voted_for': voted_for_encrypted}
        sock.sendto(json.dumps(msg).encode('utf-8'), (host, port))

        # Zero Knowledge Proof verification with the miner

        fail = 0

        for i in range(1, 6):
            msg, addr = sock.recvfrom(1024)
            msg = msg.decode('utf-8')

            if msg == "Failed":
                fail = 1
                break

            y = pow(g, voted_for, p)
            r = random.randint(0, p-1)
            h = pow(g, r, p)
            yh = str(y) + " " + str(h)
            sock.sendto(yh.encode('utf-8'), (host, port))

            b, addr = sock.recvfrom(1024)
            b = b.decode('utf-8')
            b = int(b)

            s = (r + b * voted_for)%(p-1)
            sock.sendto(str(s).encode('utf-8'), (host, port))

        if fail == 0:
            msg, addr = sock.recvfrom(1024)
            msg = msg.decode('utf-8')
            print(msg)

        viewUser(voter, voted_for_encrypted)

    # Send the vote to the trusted third party
    sock.sendto(str(voted_for).encode('utf-8'), (socket.gethostname(), trustedParty))


castVote()