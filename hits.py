import pdb
import graph
import math
import operator

    
def printTopValues(dictToPrint, outFile):
    out = open(outFile, 'w')
    for k in range(100):
    	value = ("%.6f" % round(dictToPrint[k][1],6))
    	output = str(value)+' '+str(dictToPrint[k][0])+'\n'
        out.write(output)
    out.close()


def getHubsAuth(outNodes, inNodes, HUB_FILE, AUTH_FILE, ITERATIONS):
    #set up initial Auth and Hub for all nodes
    currH = dict()		
    currA = dict()		
    #the initial value for hub and authority is 1/(sqrt(N)) for ALL nodes
    initialScore = 1.00/math.pow(len(outNodes), 0.5)
    #set up the current hub and authority values
    currA.update((x, initialScore) for x, y in inNodes.items())
    currH.update((x, initialScore) for x, y in outNodes.items())

	
    #THE ALGORITHM 
    for it in range(ITERATIONS):
        nextH = dict() #hub values for the nodes
        nextA = dict() #authority values for nodes
    
        # 1. HUB
        norm = 0 
        for origin in outNodes:
            nextH[origin] = 0
            for dest in outNodes[origin]:
                nextH[origin] += currA[dest]
            norm += math.pow(nextH[origin],2)	
        normFactor = 1.00/math.pow(norm,0.5)

        for hub in nextH:
            nextH[hub] = nextH[hub]*normFactor

        # 2. AUTHORITY
        norm = 0
        for dest in inNodes:
             nextA[dest] = 0
             for origin in inNodes[dest]:
                 nextA[dest] += nextH[origin]
             norm += math.pow(nextA[dest],2)	 
        normFactor = 1.00/math.pow(norm,0.5)
        for auth in nextA:
    	 nextA[auth] = nextA[auth]*normFactor
	
        #get ready for the next round
        currA = nextA
        currH = nextH
        
    
    listNextA = nextA.items()
    listNextH = nextH.items()
    sortedListA = sorted(listNextA, key=lambda tup: tup[1], reverse=True)
    sortedListH = sorted(listNextH, key=lambda tup: tup[1], reverse=True)
    top100A = dict(sortedListA[:100])
    top100H = dict(sortedListH[:100])
    return [top100A, top100H]

