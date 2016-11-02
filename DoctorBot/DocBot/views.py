# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import math
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect

import re
from collections import Counter

import nltk
import sys

#import editDistance as ed

from nltk.util import ngrams

from nltk.stem.lancaster import LancasterStemmer

st = LancasterStemmer()

import re

import pickle

f = open("/home/md/DoctorBot/DocBot/files/MedicalData")

AllWords = f.read().split('\n')

generalWords = ['symptoms','exams and tests','surgery','causes','treatment','description','home care']

# cold fever
given = []

# causes symptoms
toFind = []


f = open('/home/md/DoctorBot/DocBot/files/stopwords.txt')

stopwords = f.read().split(',');

mainDict = pickle.load(open('/home/md/DoctorBot/DocBot/files/newDict'))

MedicalList = []

chats=[]

def words(text): return re.findall(r'\w+', text.lower())

#WORDS = Counter(words(open('WordsDict.txt').read()))
WORDS = Counter(words(open('/home/md/DoctorBot/DocBot/files/Medicaltext').read()))
#print Counter(WORDS).most_common(10)
#print WORDS['cancer']
    
def P(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return float(WORDS[word]) / float(N)

def correction(word): 
    "Most probable spelling correction for word."
    k = candidates(word);
    print k
    return max(candidates(word), key=P)

def candidates(word): 
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))





# Create your views here.

def index(request,question_id):
	print str(request)
	
	s=""
	for i in range(int(question_id)):
		s+=str(i)+'\n'
	return HttpResponse("<h1>"+s+"</h1>")


def factorial1(request):
	print "request is ",request
	chats.append((0,request.POST['num']))
	f=processQueryByClient(request.POST['num'])
	chats.append((1,str(f)))
 	return render(request,"Fact.html",{'chats':chats})
 	#return HttpResponseRedirect("db/home")

def new(request):
	return HttpResponse("<h1>Hello</h1>")



def askQuery():

	return raw_input("Enter your query ")

# return the tokens of the query

def tokenize( query ):

	return nltk.word_tokenize(query)	


def correctTokens( tokens ):

	for i in range(len(tokens)):
		tokens[i]=correction(tokens[i]);
	pass


def filterTokens( tokens ):

	# remove stopwords
	filteredTokens = []
	for i in range(len(tokens)):
		if tokens[i]  not in stopwords:
			filteredTokens.append( tokens[i] ) 
	return filteredTokens

"""
def reCorrectTokens( tokens ):
	return
	# applying  edit distance
	for i in range(len(tokens)):
		tokens[i] =  ed.similarity( tokens[i] , AllWords ) 
"""

def fMeasure(word1, word2):
	w1_c = [0]*256
	w2_c = [0]*256
	for i in word1:
		w1_c[ord(i)] += 1 
	for i in word2:
		w2_c[ord(i)] += 1
	matched_words = 0
	for i in xrange(256):
		matched_words += min(w1_c[i], w2_c[i])
	if (matched_words == 0):
		return 99999
	return (max(len(word1), len(word2)) / float(matched_words))		


def processQuery( tokens , flexibility):
	# for 4 to 2 grams
	for gram in range(4,1,-1):
		ngramsTokens = ngrams(tokens,gram) 
	#	print ngramsTokens
		for eachGram in ngramsTokens:
			key = reduce(lambda x,y :x+" "+y,eachGram)
			if key in mainDict:
				given.append((key,mainDict[key][0]))
			"""
			else:
				stemedkey = reduce(lambda x,y :st.stem(x)+" "+st.stem(y),eachGram)
				print key
				minimum = 9999999999
				for word in mainDict:
					w = reduce(lambda x,y :st.stem(x)+" "+st.stem(y),word.split())
					fValue = min(fMeasure( w.encode('ascii', 'ignore') , stemedkey ),fMeasure(word.encode('ascii', 'ignore'),key))
					if fValue < minimum:
						minimum = fValue
						matchedWord = word

				if minimum <= flexibility*gram:
					#print matchedWord
					given.append((matchedWord,mainDict[matchedWord][0]))

			"""
			
	# for 1 grams


	for key in tokens:
		if key in mainDict:
			given.append((key,mainDict[key][0]))
		else:
			newkey = st.stem(key)
			for word in generalWords:
				if word.count(newkey)!=0:
					toFind.append(word)


def findResult():
	temps=[]
	print "Given List --- ",given
	print "To find ------",toFind
	for element in given:
		for find in set(toFind):
			if find not in mainDict[element[0]][1]:
				temps.append(find+": Not Available")
			else:
				temps.append(str(mainDict[element[0]][1][find]))
	return str(temps)

def checkAllSymptoms():
	for element in given:
		if element[1]=='d':
			return 0
	return 1
	
def findDisease():
	countDict={}
	l={}
	for element in given:
		for key in mainDict:
			if len(mainDict[key])>1 and 'symptoms' in mainDict[key][1]:
				if element[0] in mainDict[key][1]["symptoms"][1]:
					if key not in countDict:
						countDict[key]=1
					else:
						countDict[key]+=1
	l=(countDict.items())
	l.sort(key=lambda x:-x[1])
	try:
		return l[:3]
	except:
		return l

incomp=False
def processQueryByClient(query):
	print mainDict['cancer']
	global given
	global toFind
	if incomp==False:
		given=[]
		toFind=[]

	print "tokenizing"
	tokens = tokenize( query.lower() )
	print tokens
	print "Correcting tokens"
	correctTokens(tokens)
	print tokens
	print "filering tokens"
	tokens=filterTokens(tokens)
	print tokens
	print "recorrect"
	#reCorrectTokens( tokens )
	print tokens
	print "Processing Query"
	flexibility=0.55
	processQuery( tokens ,flexibility)

	print "Given list:",given

	print "To find list",toFind

	global incomp
	#to find disease from symptoms
	if toFind==[] and checkAllSymptoms() ==1:
		incomp=False
		return findDisease()
	else:
		print 'hi'
		out=findResult()
		print out
		if out=='[]':
			st="What are you searching for:\n1.Symptoms<br>2.Treatment<br/>3.Causes<br/>4.Home Care<br/>5.Tests<br/>6.Surgery"
			
			incomp=True
			return st
		else:
			incomp=False
			return out