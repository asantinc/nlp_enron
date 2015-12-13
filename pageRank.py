import pdb
import operator
import pdb


def printTopValues(dictToPrint, outFile):
    out = open(outFile, 'w')
    for k in range(100):
    	value = ("%.6f" % round(dictToPrint[k][1],6))
    	output = str(value)+' '+str(dictToPrint[k][0])+'\n'
        out.write(output)
    out.close()


def getPageRank(myGraph, sinkNodesSet, ITERATIONS, PR_FILE, LAMBDA):
    #set up initial pagerank for everyone
    currentPR = dict()
    initialPageRank = 1.00/len(myGraph)
    graphSize = len(myGraph)
    sinkPRTotal = 0                  #we need to add this to all non sinks on every iteration, but an updated version
    for node in myGraph:
        currentPR[node] = initialPageRank
        if node in sinkNodesSet:
            sinkPRTotal += initialPageRank
    randomVisit = ((1-LAMBDA)*1.00)/len(myGraph)       #add this to all nodes --> but also include sinkPR for all non sink nodes
    sinkPR = (sinkPRTotal*LAMBDA)/len(myGraph)

    nextPRSum = 0
    for node in myGraph:
        nextPRSum += currentPR[node]

    for it in range(ITERATIONS):
        nextPR = dict()

        for originNode in myGraph:

            if(len(myGraph[originNode]) > 0):           #if I'm not a sink node, donate my PR
                donatedPR = (1.00*LAMBDA*currentPR[originNode])/(len(myGraph[originNode]))
                for dest in myGraph[originNode]:
                    try:
                        nextPR[dest] += donatedPR 
                    except KeyError:
                        nextPR[dest] = donatedPR 

        for node in currentPR:                          #add the random access to page PR
            #if node not in sinkNodesSet:
            try:
                nextPR[node] += randomVisit+sinkPR
            except KeyError:
                nextPR[node] = randomVisit+sinkPR

        #recalculate the PR donated by sinks to everyone else
        sinkPRTotal = 0
        for sink in sinkNodesSet:
            sinkPRTotal += nextPR[sink]  
        sinkPR = (sinkPRTotal*LAMBDA*1.00)/len(myGraph)      
        currentPR = nextPR

        nextPRSum = 0
        for node in currentPR:
            nextPRSum += currentPR[node]
        

    nextPRList = nextPR.items()
    sortedNextPRList = sorted(nextPRList, key=lambda tup: tup[1], reverse=True)
    printTopValues(sortedNextPRList, PR_FILE)
    top100 = dict(sortedNextPRList[:100])
    return dict(top100)


