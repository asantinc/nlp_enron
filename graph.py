
def createGraph(f):
    outNodes = dict()
    inNodes = dict()
    sinkNodes = 0
    sinkNodesSet = set()
    sendReceiveDict = dict()
    with open(f, 'r') as graphFile:
        while True:
            emailLine = graphFile.readline()
            if not emailLine: break

            emailContent = emailLine.lower().split()
            emailID = emailContent[0].strip()
            origin = emailContent[1].strip()
            dest = emailContent[2].strip()
            
            if origin != dest:      #not a self link
                #OUTNODES
                if origin not in outNodes:
                    outNodes[origin] = [dest]
                else:
                    if (len(outNodes[origin]) == 0): #this used to be a sink
                        sinkNodes -= 1   
                        sinkNodesSet.remove(origin)
                    outNodes[origin].append(dest)

                if dest not in outNodes and dest not in sinkNodesSet: #might be a sink node, it should redistribute its page rank to all nodes
                    outNodes[dest] = []
                    sinkNodes += 1
                    sinkNodesSet.add(dest)
  
                #INNODES
                if dest not in inNodes:		#if we haven't inserted them yet
                    inNodes[dest] = [origin]	#we insert the first inNode
                else:
                    inNodes[dest].append(origin)	#otherwise we append it to the existing inNode list

                if origin not in inNodes: #we don't want to miss any nodes, every if they have no inNodes
                    inNodes[origin] = []
                    
                #keeping track of the emails being passed around
                if origin not in sendReceiveDict:
                    sendReceiveDict[origin] = dict()
                    sendReceiveDict[origin][dest] = [emailID]
                elif dest not in sendReceiveDict[origin]:
                    sendReceiveDict[origin][dest] = [emailID]
                else:
                    sendReceiveDict[origin][dest].append(emailID)
                    
    return [outNodes, sinkNodesSet, inNodes, sendReceiveDict]

