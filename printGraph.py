from graphviz import Digraph
import enron
import pdb

'''
Parse contents of a file into a list of tuples
'''
def parseGraphFile(fileN):
    tupleList = list()
    with open(fileN, 'r') as r:
        while True:
            line = r.readline()
            if not line: break
            components = line.split('\t')
            
            emails = components[0]
            wordList = components[1]
            emailList = emails.split()
            tup = (emailList[0], emailList[1], wordList)
            tupleList.append(tup)
    return tupleList

tupleList = parseGraphFile('graph_input.txt')
roleDict = enron.getRoles('roles.txt')
dot = Digraph(comment='Enron Emails')

nodeSet = set()  
for xchange in tupleList:
    sender = xchange[0]
    rec = xchange[1]
    keys = xchange[2]
    clean_sender = sender.split('@')[0]
    clean_rec = rec.split('@')[0]
    pdb.set_trace()
    if clean_sender in roleDict:
        clean_sender+= ', '+roleDict[clean_sender]
    if clean_rec in roleDict:
        clean_rec+= ', '+roleDict[clean_rec]
    if clean_sender not in nodeSet:
        nodeSet.add(clean_sender)
        dot.node(clean_sender, clean_sender)
    if clean_rec not in nodeSet:
        nodeSet.add(clean_sender)
        dot.node(clean_rec, clean_rec)
    dot.edge(clean_sender, clean_rec, label=keys)

dot.render('test-output/enron.gv', view=True)
    
        
        
        
        
        
        
    