# Import to handle command line arguments
import argparse
import sys
from math import ceil

# Custom class for the finite state automata
class State(object):
	def __init__(self, id, level = 0, transitions = {'0': 'null', '1': 'null'}, failure = "null"):
		self.id = id
		self.level = level
		self.transitions = transitions
		self.failure = failure

def cli_progress_test(end_val, bar_length=20):
    for i in range(0, end_val):
        percent = float(i) / end_val
        hashes = '#' * int(round(percent * bar_length))
        spaces = ' ' * (bar_length - len(hashes))
        sys.stdout.write("\rPercent: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
        sys.stdout.flush()

# Encodes Word using anti-dictionary AD
# Returns (Length of original word, Encoded word)
# Length of original word is used for decoding
def Encode(AD, Word):
	v = "" # Covered prefixes
	g = "" # Compressed word
	c = 0
	per = 0
	lastper = 0
	l = len(Word)
	for a in Word:
		c = c + 1
		per = ceil(float(c / l) * 100.0)
		if per > lastper:
			lastper = per
			print(str(per) + "%")

		if len(v) > 0:
			flag = True
			for Index in range(len(v) - 1, 0, -1):
				u = v[Index:]
				if ((u + "0") in AD or (u + "1") in AD):
					flag = False
			if flag:
				g += a
		else:
			if ("0" not in AD and "1" not in AD):
				g += a
		v += a
	return(g, len(Word))

# Decodes g using anti-dictionary AD
# Returns original word of length n
def Decode(AD, g, n):
	v = "" # Decompressed word
	pos = 0 # Current position at encoded data
	while len(v) < n:
		if len(v) > 0:
			flag = True
			for Index in range(len(v) - 1, 0, -1):
				u = v[Index:]
				if (u + "0") in AD:
					v += "1"
					flag = False
					break
				if (u + "1") in AD:
					v += "0"
					flag = False
					break
			if flag:
				v += g[pos]
				pos += 1
		else:
			if ("0" in AD):
				v += "1"
			elif ("1" in AD):
				v += "0"
			else:
				v += g[pos]
				pos += 1
	return v	

# Builds a trie with all the factors of max length k of the word
c = 1	# Counter for keeping track of nodes
def BuildFact(word, k):
	Q = [State("q0")]
	p = State("q0")
	for a in word:
		p = Next(Q, p, a, k)
	return Q

# Helper of the BuildFact function
def Next(Q, p, a, k):
    global c
    if d(p, a) != "undefined":
        return d(p, a)
    elif p.level == k:
        return Next(Q, f(p), a, k)
    else:
        q = State("q" + str(c), p.level + 1)
        c += 1
        p.transitions[a] = q
        q.transitions = {'0': 'null', '1': 'null'}
        if (p.id == "q0"):
            q.failure = Q[0]
        else:			
            q.failure = Next(Q, f(p), a, k)
        Q.append(q)
        return q

# Returns the next state of p using symbol a
def d(p, a):
	if a in p.transitions:
		if p.transitions[a] == "null":
			return "undefined"
		else:
			return p.transitions[a]

# Returns the state of the failure function 	
def f(p):
	return p.failure

# Builds the anti-dictionary combining the forbidden words that get generated from the trie Q
def BuildAD(Q):
    MFW = []
    GetMFW(Q[0], "", MFW)
    return MFW

# Returns True only if the state p of a trie has no other children states
def isLeaf(p):
    return (p.transitions['0'] == "null" and p.transitions['1'] == "null")

# Recursively goes through all children of state p and outputs all forbidden words to MFW
def GetMFW(p, cur, MFW):
    if isLeaf(p) == False:
        if p.transitions['0'] != "null":
            GetMFW(p.transitions['0'], cur + '0', MFW)
        else:
            MFW.append(cur + '0')
        if p.transitions['1'] != "null":
            GetMFW(p.transitions['1'], cur + '1', MFW)
        else:
            MFW.append(cur + '1')

# Parse the arguments given via the command line
parser = argparse.ArgumentParser(description='Command line tool to compress binary string using anti-dictionaries')
parser.add_argument('-i', '--input', help='File to compress', required=True)
args = parser.parse_args()

# Local variables to store the arguments
Word = ""
bytes_read = open(args.input, "rb").read()
for b in bytes_read:
    byte = '{0:07b}'.format(b)
    Word += byte

Length = 8

# Actual process and statistics
print("Building anti-dictionary")
Anti = BuildAD(BuildFact(Word, Length))
with open('anti.dat', 'w') as file:
    for fw in Anti:
        file.write(fw + "\n")
print("Line separated anti-dictionary saved on disk as 'anti.dat'")
print("Compressing file. This will take some time")
Result = Encode(Anti, Word)
with open('compressed.dat', 'w') as file:
    file.write(str(Result[1]) + "\n")
    for w in Result[0]:
        file.write(w)
print("Compressed file saved on disk as 'compressed.dat'")
print("Saved " + str(Result[1] - len(Result[0])) + " digits in compression")
Size = 0
for FW in Anti:
    Size += len(FW)
print("Anti-dictionary size w/o split chars or size prefix : " + str(Size) + " digits")
print("Program end")