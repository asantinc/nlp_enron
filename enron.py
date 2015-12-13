import graph
import pageRank
import hits
import re
import visualize
import operator
from nltk.stem.porter import *

ITERATIONS = 10
LAMBDA = 0.8
GRAPH = 'graph.txt'
TEST = 'test1'
PR_FILE = 'pr.txt'
HUB_FILE = 'hubs.txt'
AUTH_FILE = 'auth.txt'
IDF = 'idf.txt'
ROLES = 'roles.txt'
EMAILS = 'subject.txt'
QUERY = 'california bankrupt risk investigation downgrade credit Dynegy junk SEC Andersen accounting'  
FINAL_OUTPUT = 'graph_input.txt'
PRODUCE_GRAPH = False

'''
Get Employee roles
'''
def getRoles(rolesFile):
    rolesDict = dict()
    with open(rolesFile, 'r') as r:
        while True:
            line = r.readline()
            if not line: break
            
            components = re.split(r"\s{2,}", line)
            email_name = re.split(r'\t+', components[0])  
            email = email_name[0].strip()
            if(len(components) == 3):
                role = components[1].strip()+' '+components[2].strip()
            elif (len(components) == 2):
                role = components[1].strip()
            else:
                role = 'Unknown'
            rolesDict[email] = role
    return rolesDict
'''
Get the subject lines and associated email ID
'''

def getEmailSubjects(emailFile):
    emailSubjectDict = dict()
    with open(emailFile, 'r') as f:
        while True:
            line = f.readline()
            if not line: break
    
            components = re.split(r"\s{2,}", line)
            emailID = components[0].strip()
            email = components[1].strip()
            emailSubjectDict[emailID] = email
    return emailSubjectDict

'''
Output IDF calculated from subject lines into an output file for quick reuse
'''
def printIDF(myIDFDict, fname):
    f = open(fname, 'w')
    for ID in myIDFDict:
        output = str(ID)+' '+str(myIDFDict[ID])+'\n'
        f.write(output)
    f.close()

'''
Parse contents of a file into a dictionary
'''
def parseFile(fileN, flipped):
    myDict = dict()
    with open(fileN, 'r') as r:
        while True:
            line = r.readline()
            if not line: break
            components = line.split()
            
            if not flipped:
                key = components[0]
                value = float(components[1])
                myDict[key] = value
            else:
                key = components[1]
                value = float(components[0])
                myDict[key] = value
    return myDict

'''
Identify high IDF words in a text
'''
def getImportantWords(email, myIDF, stemmer):
    stemTokenDict = dict()
    tokens = visualize.getTokens(email)
    stems = visualize.stem_tokens(tokens, stemmer)
    for i in range(len(stems)): #create stemToken association so we can recover the tokens from the stems
        stem = stems[i]
        token = tokens[i]
        stemTokenDict[stem] = token
    valueDict = dict()
    for stem in stems:
        if stem in myIDF:
            if (stem in valueDict) and (len(stemTokenDict[stem])>2):      
                valueDict[stem] += myIDF[stem]
            else:
                valueDict[stem] = myIDF[stem] 
    return sorted(valueDict.items(), key=operator.itemgetter(1), reverse=True), stemTokenDict    

'''
Print out final pairs and their key communication terms
'''
def outputPairs(chosenPairs, pairs, jointEmailsDict, myIDF):
    pairFile = open(FINAL_OUTPUT, 'w')
    stemmer = PorterStemmer()
    for hashKey in chosenPairs:
        pair = pairs[hashKey]
        output = pair[0]+' '+pair[1]
        email = jointEmailsDict[hashKey]
        sorted_words, stemTokenDict = getImportantWords(email, myIDF, stemmer)
        sorted_words = [stemTokenDict[x[0]] for x in sorted_words]
        best_10_words = sorted_words[:10]                       #get the top 10 words based on frequency and IDF
        keywords = ' '.join(best_10_words)
        output += '\t'+keywords+'\n'
        pairFile.write(output)
    pairFile.close()
         

if __name__ == '__main__':

    #get Enron graph
    [outNodes, sinkNodesSet, inNodes, sendReceiveDict] = graph.createGraph(GRAPH)

    #PAGERANK and HITS
    [AuthDict, HubDict] = hits.getHubsAuth(outNodes, inNodes, HUB_FILE, AUTH_FILE, ITERATIONS)
    pagerankDict = pageRank.getPageRank(outNodes, sinkNodesSet, ITERATIONS, PR_FILE, LAMBDA)
    
    #This part is useless unless GraphViz is installed
    if PRODUCE_GRAPH == True:
        #Take the union of people
        tempSet = set(pagerankDict.keys()).union(set(AuthDict.keys()))
        importantEmployees = tempSet.union(HubDict.keys())          #list of all emails of the important people 
        #Remove useless pete davis
        importantEmployees.remove('pete.davis@enron.com')     

        #ROLES and EMAILS passed around
        roleDict = getRoles(ROLES)     
        emailSubjectDict = getEmailSubjects(EMAILS)

        #get all the emails being sent between important people
        jointEmailsDict = dict()                     #will access this with hash = 'origin'+'dest'
        pairs = dict()
        counter = 0
        for origin in importantEmployees:
            print counter
            counter += 1
            destinations = outNodes[origin]
            destList = [x for x in destinations if x in importantEmployees]
            for dest in destList:
                emailIDs = sendReceiveDict[origin][dest]
                hashValue = origin+dest
                jointEmails = ''
                for ID in emailIDs:
                    if ID in emailSubjectDict: #some email IDs do not have subjects associated with them
                        jointEmails += ' '+emailSubjectDict[ID]
                jointEmailsDict[hashValue] = jointEmails
                pairs[hashValue] = (origin, dest)


        #get IDF
        myIDF = parseFile(IDF, False)  #I parsed the entire document set and stored the idf value to file
        #returns a set of emails with grades sorted on their grade for the tf.idf of their content
        emailValuesDict, importantWordsDict = visualize.processEmails(jointEmailsDict, myIDF, QUERY)

      
        sortEmailValuePairs = sorted(emailValuesDict.items(), key=operator.itemgetter(1), reverse=True)
        receivers = set()
        uniquePeopleSet = set()
        chosenPairs = set()
        comm = 0        #counter into the sorted communications
        #who are the pairs? need it for the hash access 
        favPairs = list()
        while len(uniquePeopleSet)<12:    #get at least 15 people
            hashKey = sortEmailValuePairs[comm][0]
            communicators = pairs[hashKey]
            email = jointEmailsDict[hashKey]
            comm += 1
            uniquePeopleSet.add(communicators[0])
            uniquePeopleSet.add(communicators[1])
            receivers.add(communicators[1])
            chosenPairs.add(hashKey)
        
        #now we want to add outgoing edges from the receivers as well
        addHashPairs = list()
        for A in receivers:
            candidates = list()
            for B in uniquePeopleSet:
                if A != B:
                    hashKey = A+B
                    if hashKey in emailValuesDict:
                        tupleCand = (hashKey, emailValuesDict[hashKey])
                        candidates.append(tupleCand)
            sortCandidates = sorted(candidates, key=operator.itemgetter(1), reverse=True)
            if len(sortCandidates) > 1:
                addHashPairs.append(sortCandidates[1])      #get the second best communication with someone else in the group
        addHashPairs = [x for (x, y) in addHashPairs]
        outputPairs(list(chosenPairs)+addHashPairs, pairs, jointEmailsDict, myIDF)
    












    
