# A trusted third party to count the votes
import socket

num = 4
votes = [0, 0, 0, 0, 0]

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((socket.gethostname(), 29171))

# Run the election process till all the votes have been processed
# In a real life scenario
def runElection():
    cnt = 0
    while cnt < num:
        vote, addr = sock.recvfrom(1024)
        vote = vote.decode('utf-8')
        vote = int(vote)
        votes[vote] += 1
        cnt += 1

    print("The results of the election are: ")
    for i in range(0, 5):
        print("Candidate", i, ":", votes[i], sep = ' ')

    maxCandidate = 0

    for i in range(1, 5):
        if votes[maxCandidate] < votes[i]:
            maxCandidate = i

    # Declare the results of the election
    print("Candidate", maxCandidate, "has won the election!", sep = ' ')

runElection()