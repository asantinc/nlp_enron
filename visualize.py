import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import *
import re
import math
import pdb
import string



def averageLen(emailDict):
    lengths = [len(emailDict[i]) for i in emailDict]
    if len(lengths) == 0:
        return 0
    else:
        return (float(sum(lengths)) / len(lengths)) 

'''
Return list of tokens without stop words
'''
def getTokens(email):
    COMMON_WORDS = ['meeting' , 'paper', 'comments', 'conference', 'call']
    lowers = email.lower()
    clean_lowers = lowers.translate(None, string.punctuation)
    tokens = nltk.word_tokenize(clean_lowers)
    stop = stopwords.words('english')+COMMON_WORDS
    tokensNoStop = [w for w in tokens if w not in stop]
    return tokensNoStop

'''
Stem a list of tokens
'''
def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

'''
Method that creates the tfidf.txt file from the documents in subject.txt
'''
def getIDF(emails):
    myVocabulary = dict()	 
    myIDF = dict()		
    emailNumber = len(emails)
    threshold = 0.9*(emailNumber)
    for i in range(len(emails)):
        print i
        email = emails[i]
        tokens = getTokens(email)
        stemmer = PorterStemmer()
        stemmed = stem_tokens(stemmer)
        for token in stemmed:
            if token in myVocabulary:       #in how many docs the token appears
                myVocabulary[token] += 1
            else:
                myVocabulary[token] = 1
    for word in myVocabulary:
        occurrences = myVocabulary[word]
        if (occurrences > 3) and (occurrences<threshold):   #ignore typos and overly common words       
            myIDF[word] = math.log((emailNumber*1.00)/occurrences)
    return myIDF


'''
Returns a token: frequency dictionary for a list of tokens
'''
def getWordFrequency(tokens, myIDF):
    tokenFreqDict = dict()
    totalTokens = 0
    for token in tokens:
        if (token in myIDF):
            totalTokens += 1
            if token in tokenFreqDict:
                tokenFreqDict[token] +=1
            else:
                tokenFreqDict[token] = 1  
    return tokenFreqDict, totalTokens        

'''
Rates a set of emails based on the tf.idf of their content
'''
def processEmails(emailDict, idfDict, query):
    docValues = dict()
    importantWordsDict = dict()
    averageDocLength = averageLen(emailDict)
    k = 2
    query_tokens = getTokens(query)
    stemmer = PorterStemmer()
    query_stems = stem_tokens(query_tokens, stemmer)
    
    for originDestKey in emailDict:
        value = 0
        importantWordsDict[originDestKey] = list()   
        email = emailDict[originDestKey]
        
        email_tokens = getTokens(email)
        email_stems = stem_tokens(email_tokens, stemmer)
        tokenFreqDict, docLength = getWordFrequency(email_stems, idfDict)
        for token in tokenFreqDict:
            if token in query_stems:
                idf = idfDict[token]
                freq = tokenFreqDict[token]
                damping = ((float(k)*(docLength)) / averageDocLength) 
                importantWordsDict[originDestKey] = (token, value)
                value += (float(freq) / (freq+damping) ) * idf
        docValues[originDestKey] = value
    return docValues, importantWordsDict
    


