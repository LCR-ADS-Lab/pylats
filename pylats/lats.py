#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 10:35:53 2021

@author: kristopherkyle

"""
version = ".57" #Add more detailed normalization options
#need to test numbers.
import math
import os
import pickle
import json
import glob
import lzma
from operator import itemgetter
import statistics as stat
from collections import Counter
import pkg_resources #for importing data from packages
from os.path import exists
from taaled import lexdiv as ld
from pathlib import Path #windows + mac compatibility

#load datafiles
def get_fname(packagename,filename): #look in package, then in local working directory
	try: 
		data_filename = pkg_resources.resource_filename(packagename, filename)
		#print(data_filename)
	except (ModuleNotFoundError, TypeError, FileNotFoundError):
		print("NOTE:",filename,"not found in package, using local file")
		data_filename = filename
	if exists(data_filename):
		return(data_filename)
	else:
		print("NOTE:",filename,"not found in package, using local file")
		return(filename)

# en_rwl = pickle.load(open(get_fname('pylats',"real_words5.pickle"),"rb")) #words in written COCA that occur at least 5 times
# es_rwl = json.load(open(get_fname('pylats',"corp_raw_freq_escow_ax01_2021-04-28_5.json")))
# en_10kpos = pickle.load(open(get_fname('pylats',"10k_pos_noes.pickle"),"rb")) #words in COCA that are within the most frequent 10k
# en_10kraw = pickle.load(open(get_fname('pylats',"10k_raw_noes.pickle"),"rb")) #words in COCA that are within the most frequent 10k
# cedel_ignore = pickle.load(open(get_fname('pylats',"cedel_ignore.pickle"),"rb")) #words in the CEDEL L2 Spanish (L1 English) corpus that should be ignored but were not caught by other filters
def lTod(l):
	outd = {}
	for x in l:
		outd[x] = None
	return(outd)

en_rwl = pickle.load(open("real_words5.pickle","rb")) #words in written COCA that occur at least 5 times
es_rwl = json.load(open("corp_raw_freq_escow_ax01_2021-04-28_5.json",encoding="utf-8"))
en_10kpos = pickle.load(open("10k_pos_noes.pickle","rb")) #words in COCA that are within the most frequent 10k
en_10kraw = pickle.load(open("10k_raw_noes.pickle","rb")) #words in COCA that are within the most frequent 10k
cedel_ignore = pickle.load(open("cedel_ignore.pickle","rb")) #words in the CEDEL L2 Spanish (L1 English) corpus that should be ignored but were not caught by other filters



statusd = {"spld":False,"mdld":False,"models" : []} #for updating and maintaining load statuses

def load_model(paramName): # this is an attempt to get a module to load easily
	print("Attempting to load spacy model:", paramName.model)
	if statusd["spld"] == True: #if spacy has been successfully loaded
		try:
			paramName.nlp = spacy.load(paramName.model) #try to load model
			statusd["mdld"] = True #set dictionary value
			statusd["models"].append(paramName.model) #set dictionary value
			print("Successfully loaded spacy model:",paramName.model)
		except OSError:
			print("The selected model <",paramName.model,"> does not seem to be available on your system.\nPlease load a different model or see Spacy documentation for assistance.")
	else:
		print("You cannot load a Spacy model because pylats was not able to import Spacy. This most likely means that Spacy is not installed on your system.")
	# if statusd["mdld"] == False:
	# 	nlp = None
	# return(nlp)

try: 
	import spacy
	statusd["spld"] = True
except ModuleNotFoundError:
	print("Spacy has not been installed.\nTo access pylats advanced features for English, French, or Spanish please install Spacy.")
	statusd["spld"] = False

# if statusd["spld"] == True:
# 	try:
# 		nlp_en_sm = spacy.load("en_core_web_sm")
# 		statusd["models"].append("en_core_web_sm")
# 	except OSError:
# 		print("The selected model <",modelname,"> does not seem to be available on your system.\nPlease load a different model or see Spacy documentation for assistance.")
# 		if statusd["mdld"] == False:
# 			statusd["mdld"] = False

# nlp_en_sm = load_model("en_core_web_sm")
# nlp_en_trf = load_model("en_core_web_trf")
# nlp_es_sm = load_model("es_core_news_sm")
# nlp_es_trf = load_model("es_dep_news_trf")

#default parameters
class EnSmp:
	sp = False #use spacy?
	model = None
	nlp = None #for spacy
	splitter = "\n" #paragraph splitter
	sspl = "simple" #sentence split
	punctse = [".","?","!"]

class EnSm:
	sp = True
	model = "en_core_web_sm"
	splitter = "\n"
	nlp = None
	sspl = "spacy"
	punctse = [".","?","!"]

class EnTrf:
	sp = True
	model = "en_core_web_trf"
	splitter = "\n"
	nlp = None
	sspl = "spacy"
	punctse = [".","?","!"]

class EsTrf:
	sp = True
	model = "es_dep_news_trf"
	splitter = "\n"
	nlp = None
	sspl = "spacy"
	punctse = [".","?","!"]

class FrTrf:
	sp = True
	model = "fr_dep_news_trf"
	splitter = "\n"
	nlp = None
	sspl = "spacy"
	punctse = [".","?","!"]

#other parameters:
class EnDefault:
	lang = "en"
	punctuation = ['``', "''", "'", '.', ',', '?', '!', ')', '(', '%', '/', '-', '_', '-LRB-', '-RRB-', 'SYM', ':', ';', '"']
	punctse = [".","?","!"]
	abbrvs = ["mrs.","ms.","mr.","dr.","phd."]
	splitter = "\n" #for splitting paragraphs
	rwl = en_rwl
	sp = True
	sspl = "spacy"
	removel = ['becuase'] #typos and other words not caught by the real words list
	attested = True #filter output using real words list?
	spaces = [" ","  ","   ","    "] #need to add more here
	override = [] #items the system ignores that should be overridden
	posignore = ["PROPN"] #ignore proper nouns
	numbers = ["NUM"] #pos_ tag for numbers
	wordConnect = "_"
	ngramConnect = "__" #for connecting ngrams
	contentPOS = ["VERB","NOUN","PROPN","ADJ","ADV"] #note that PROPN will be overridden by posignore in this case
	advMannerSuff = ["ly"]
	advMannerLex = ["well"]
	includeCwFw = True
	contentLemIgnore = [] #can be added, blank for now
	deprels = ["nsubj","dobj","amod","advmod"]
	depOrder = "dep2head" #options are "dep2head" or "orderofA"
	lemma = True
	lower = True #treat all words as lower case
	pos = "upos" #other options are "pos" for Penn tags and "upos" for universal tags
	morphs = None #can also be None
	morphsExtra = None #for more complicated situations

class EsDefault: #these are for the Spanish parameters - these need to be updated
	lang = "es"
	punctuation = ['``', "''", "'", '.', ',', '?', '!', ')', '(', '%', '/', '-', '_', '-LRB-', '-RRB-', 'SYM', ':', ';', '"','¿','¡','”','“','…',"--","–","»","]","["]
	punctse = [".","?","!"]
	abbrvs = [] #these can be added
	splitter = "\n" #for splitting paragraphs
	rwl = es_rwl
	sp = True
	sspl = "spacy"
	removel = lTod(en_10kraw + en_10kpos + cedel_ignore) #typos and other words not caught by the real words list also, frequent English words that may occur in L2 corpora may need to filter these
	attested = True #filter output using real words list?
	spaces = [" ","  ","   ","    "]  #need to add more here
	override = [] 
	posignore = ["PROPN"] #proper nouns and numbers. Note that some numbers are missed. Need to fix.
	numbers = ["NUM"] #pos_ tag for numbers - an empty list [] will indicate that numbers are included
	wordConnect = "_"
	ngramConnect = "__" #for connecting ngrams
	contentPOS = ["VERB","NOUN","PROPN","ADJ","ADV"] #note that PROPN will be overridden by posignore in this case
	advMannerSuff = ["mente"]
	advMannerLex = ["bien", "mal", "despacio", "mejor", "peor", "rápido", "lento", "fuerte", "alto", "bajo", "suave"]
	includeCwFw = True
	contentLemIgnore = ["ser","estar"] #note that these are actually already ignored because they are tagged as "AUX"
	deprels = ["nsubj","obj","amod","advmod"] #add compound? (noun-noun combinations)
	depOrder = "dep2head" #options are "dep2head" or "orderofA"
	lemma = True #lemmatize word form?
	lower = True #treat all words as lower case?
	pos = "upos" #options are "xpos","upos", or None
	morphs = ["Mood","Tense"] #can also be None - Add morphological information to words?
	morphsExtra = None #for more complicated situations

class FrDefault: #For French.#Eva is using 3.7.6;TRF 3.7.2 - Kris is currently using 3.7.2
	lang = "fr"
	punctuation = ['.', ',', '?', '!', ':', ';', "'", '"', "‘", "’", '“', '”', "«", "»", '/', '-', '—', '_', '...', '…', '(', ')', '[', ']', '{', '}', '%', '&', '$', '€', '£', '@', '*', '#']
	punctse = [".","?","!"]
	abbrvs = [] #these can be added
	splitter = "\n" #for splitting paragraphs
	rwl = None #es_rwl # need to update this
	sp = True
	sspl = "spacy"
	removel = [] #for ignoring particular words
	attested = True #filter output using real words list?
	spaces = [" ","  ","   ","    "]  #need to add more here?
	override = [] 
	posignore = ["PROPN","SPACE"] #Which POS to ignore? Kris + Eva decided to ignore proper nouns (2025-03-17)
	numbers = ["NUM"] # None is also OK #pos_ tag for numbers; Kris and Eva decided to see if we can exclude digits but include written words.
	wordConnect = "_"
	ngramConnect = "__" #for connecting ngrams
	contentPOS = ["VERB","NOUN","PROPN","ADJ","ADV"] #note that PROPN will be overridden by posignore in this case; Kris and Eva discussed including only "ment" ending adverbs (+ short list?)
	contentLemIgnore = [] #Kris + Eva determined that "être" is usually Aux (and can be ignored then)
	advMannerSuff = ["ment"]
	advMannerLex = ["bien","mieux","mal","pire","vite","fort"]
	includeCwFw = True
	deprels = ["nsubj","obj","amod","advmod"]
	depOrder = "dep2head" #options are "dep2head" or "orderofA"
	lemma = True
	lower = True #treat all words as lower case
	pos = "upos" #other options are "pos" for fine-grained tags,"upos" for universal tags, or None - (these are the same in French)
	morphs = ["Mood","Tense"] #can also be None
	morphsExtra = [{"key":"VerbForm","value":"Part","morphs":["Gender","Number"]}] #for more complicated situations

class TokObject():
	def __init__(self, token = None,counter = 0,charD = None): #see parameters object for all relevant variables
		self.idx = counter #position in sentence
		self.preIgnore = False #This will be the preprocessing ignore indicator
		self.preIgnoreReasons = []
		self.indexIgnore = False #This will be for exclusion based on database (or other constraints)
		if "spacy" in str(type(token)): #check for spacy token
			self.text = token.text #raw text
			self.textlow = token.text.lower()
			self.lemma = token.lemma_ #raw text #lemma form (same as spacy)
			self.upos = token.pos_ #Universal pos tag (same as spacy)
			self.xpos = token.tag_
			self.morph = str(token.morph)
			self.deprel = token.dep_ #dependency relationship (same as spacy)
			if charD != None:
				self.idxHead = charD[token.head.idx]
			else:
				self.idxHead = None
			self.nchars = len(token.text) #length of item in chars
			self.cwfw = None #for content word/function word assignment
			self.tokOut = None
			self.bgOut = None
			self.depbgOut = None

		else:
			self.text = token
			if token == None:
				self.textlow = None
			else:
				self.textlow = token.lower()
			self.lemma = None #raw text #lemma form (same as spacy)
			self.upos = None #Universal pos tag (same as spacy)
			self.xpos = None
			self.morph = None
			self.deprel = None #dependency relationship (same as spacy)
			self.idxHead = None
			if token == None:
				self.nchars = None
			else:
				self.nchars = len(self.text) #length of item in chars
			self.cwfw = None #for content word/function word assignment
			self.tokOut = None
			self.bgOut = None
			self.depbgOut = None

			#print("Error: Expected spacy token or string, got", str(type(token)),"instead")
		self.attrs = {} #attributes can be added to this as needed
		#real words

class preProcessConllu:
	def conllu2tokp(self,conlluText):
		paras = []
		para = []
		for sent in conlluText.split("\n\n"):
			if len(sent) < 1:
				continue
			#print(sent)
			sentToks = []
			for token in sent.split("\n"):
				#print(token)
				tok = TokObject()
				tokInfo = token.split("\t")
				tok.idx = int(tokInfo[0])
				tok.text = tokInfo[1]
				tok.textlow = tokInfo[1].lower()
				tok.lemma = tokInfo[2].lower()
				tok.upos = tokInfo[3]
				tok.xpos = tokInfo[4]
				tok.morph = tokInfo[5]
				tok.idxHead = int(tokInfo[6])
				tok.deprel = tokInfo[7]
				tok.nchars = len(tokInfo[1])
				sentToks.append(tok)
			para.append(sentToks)
		paras.append(para)
		return(paras)
			

	def para2sent(self,paratok):
		senttoks = []
		for paras in paratok: #iterate through paragraphs
			for sent in paras:
				senttoks.append(sent)
		return(senttoks)

	def sent2tok(self,senttok):
		return([y for x in senttok for y in x])

	def __init__ (self, text = None):
		#print(param.abbrvs)
		if text == None:
			self.paras = None
			self.sents = None
			self.toks = None
			self.paratxt = None
			self.senttxt = None
			self.toktxt = None
		else:
			#self.tokens = self.text2tok(text) #tokenized data
			self.parasto = self.conllu2tokp(text) #TokObject tokens ([[[]]]) [para[sent[tok]]]
			self.sentsto = self.para2sent(self.parasto) #TokObject tokens ([[]]) [sent[tok]]
			self.toksto = self.sent2tok(self.sentsto) #TokObject tokens ([]) [tok]

class preProcess:
	def text2tok(self,text, params): #punctuation defaults to the params class definition.
		#punctuation = params.punctuation,realwords = params.rwl, sp = params.sp
		counter = 0	
		tok_text = []
		if params.sp == False: #basic (language agnostic) whitespace tokenizer 
			text = text.replace("\n"," ")
			spl_text = text.split(" ")
			for token in spl_text:
				#print(token)
				if len(token) == 0:
					continue
				#print(token)
				tok_text.append(TokObject(token,counter))
				counter +=1
		else: #if sp == True, rely on Spacy for tokenization
			text = text.replace("\n"," ")
			for token in params.nlp(text):
				tok_text.append(TokObject(token,counter))#realwords relies on a global variable
				counter+=1
		return(tok_text)

	def text2sent(self, text, params):
		sents = []
		for x in text.split("\n"): #check for text separated by newline characters first
			if len(x) == 0:
				continue
			pre_sent = [] #holder for tokens included in each sentence
			for tok in x.split(" "):
				if len(tok) == 0:
					continue
				if tok not in params.punctse:
					pre_sent.append(tok)
			if len(pre_sent) != 0:
				sents.append(" ".join(pre_sent))
		return(sents)

	#pipeline for sentences and tokens
	def text2toks(self, text, params): #sspl options include: spacy, simple - will add more in the future
		#punctse = params.punctse,punctuation = params.punctuation, realwords = params.rwl, sp = params.sp, sspl = params.sspl
		tok_texts = []
		if params.sp == True: #message if spacy is selected but not available
			if statusd["spld"] == False or params.nlp == None: #global variable that indicate whether spacy itself has been loaded
				print("Spacy processing selected, but either spacy and/or the spacy nlp model is not available. Defaulting to simple rule-based tokenization.")
				params.sp = False
				params.sspl = "simple" #this is not ideal in this case
		
		if params.sp == True:
			if params.sspl == "spacy":
				doc = params.nlp(text)
				for sent in doc.sents:
					counter = 0
					charD = {}
					for token in sent:
						charD[token.idx] = counter
						counter +=1
					toks = []
					counter = 0 #reset counter
					for token in sent:
						toks.append(TokObject(token, counter,charD))
						counter +=1
					tok_texts.append(toks)
			if params.sspl == "simple":
				for sent in self.text2sent(text, params):
					tok_texts.append(self.text2tok(sent,params))

		else:
			for sent in self.text2sent(text, params):
				tok_texts.append(self.text2tok(sent, params))
		return(tok_texts)

	#paragraph tokenize - rule based method of splitting a string into paragraph strings. By default, presumes that paragraphs are separated by "\n"
	def text2para(self, text, params):
		paras = []
		for x in text.split(params.splitter):
			if len(x) == 0:
				continue
			else:
				paras.append(x)
		return(paras)
		#pipeline for paragraph, sentences, and tokens
	def text2tokp(self,text, params):
		tok_texts = []
		for para in self.text2para(text, params):
			tok_texts.append(self.text2toks(para, params))
		return(tok_texts)
	
	def para2sent(self,paratok):
		senttoks = []
		for paras in paratok: #iterate through paragraphs
			for sent in paras:
				senttoks.append(sent)
		return(senttoks)

	def sent2tok(self,senttok):
		return([y for x in senttok for y in x])

	def __init__ (self, text = None, params = EnSmp):
		#print(param.abbrvs)
		if text == None:
			self.paras = None
			self.sents = None
			self.toks = None
			self.paratxt = None
			self.senttxt = None
			self.toktxt = None
		else:
			#self.tokens = self.text2tok(text) #tokenized data
			self.parasto = self.text2tokp(text,params) #TokObject tokens ([[[]]]) [para[sent[tok]]]
			self.sentsto = self.para2sent(self.parasto) #TokObject tokens ([[]]) [sent[tok]]
			self.toksto = self.sent2tok(self.sentsto) #TokObject tokens ([]) [tok]

	advMannerSuff = ["ment"]
	advMannerLex = ["bien","mieux","mal","pire","vite","fort"]
	contentPOS = ["VERB","NOUN","PROPN","ADJ","ADV"] #note that PROPN will be overridden by posignore in this case
	advMannerSuff = ["mente"]
	advMannerLex = ["bien", "mal", "despacio", "mejor", "peor", "rápido", "lento", "fuerte", "alto", "bajo", "suave"]

class Normalize:
	def advMannerCheck(self,token,params):
		mannerCheck = False
		if token.upos in ["ADV"]:
			for suff in params.advMannerSuff:
				if token.textlow[-len(suff):] == suff:
					mannerCheck = True
			if token.textlow in params.advMannerLex:
				mannerCheck = True
		return(mannerCheck)

	def tokProcess(self,fl_paras, params):
		normalized = []
		for para in fl_paras:
			sents = []
			for sent in para:
				toks = []
				for token in sent:
					if token.text in params.punctuation:
						token.preIgnore = True
						token.preIgnoreReasons.append("Punctuation")
						toks.append(token)
						continue
					if params.posignore != None: 
						if token.xpos in params.posignore or token.upos in params.posignore:
							token.preIgnore = True
							token.preIgnoreReasons.append("Ignore POS")
							toks.append(token)
							continue
					if params.numbers != None:
						if token.xpos in params.numbers or token.upos in params.numbers:
							token.preIgnore = True
							token.preIgnoreReasons.append("Ignore Numbers")
							toks.append(token)
							continue
					if params.rwl != None:
						if token.text.lower() not in params.rwl and token.lemma.lower() not in params.rwl:
							token.preIgnore = True
							token.preIgnoreReasons.append("Not in real word list")
							toks.append(token)
							continue
					#print(token.text)	
					if token.text.lower() in params.removel or token.lemma.lower() in params.removel:
							token.preIgnore = True
							token.preIgnoreReasons.append("Word in ignore list")
							toks.append(token)
							continue
					if params.contentPOS != []:
						if token.xpos in params.contentPOS or token.upos in params.contentPOS:
							if token.lemma not in params.contentLemIgnore:
								if token.upos in ["ADV"]:
									if self.advMannerCheck(token,params) == True:
										token.cwfw = "cw"
									else:
										token.cwfw = "fw"
								else:
									token.cwfw = "cw"
							else:
								token.cwfw = "fw"
						else:
							token.cwfw = "fw"

					if token.preIgnore == False:
						tokOutL = []
						if params.lemma == False:
							preTok = token.text
						else:
							preTok = token.lemma
						if params.lower == False:
							tokOutL.append(preTok)
						else:
							tokOutL.append(preTok.lower())
						if params.pos != None:
							if params.pos == "upos":
								tokOutL.append(token.upos)
							if params.pos == "pos":
								tokOutL.append(token.xpos)

						if params.morphs != None: #updated in version .57 on 2026-03-09
							#print(str(token.morph))
							if token.morph not in [None,""," "]:
								morph_list = []
								morphs = str(tag_string).split("|") #split the morphology output into a list
								morphDict = {}
								for x in morphs:
									item = x.split("=")
									morphDict[item[0]] = item[1]
								for m in params.morphs:
									if m in morphDict:
										morph_list.append(morphDict[m])
								#convMorph = [x.split("=")[1] for x in token.morph.split("|") if x.split("=")[0] in params.morphs]
								refinedMorph = [x for x in morph_list if x not in [""]]
								if len(refinedMorph) >= 1:
									tokOutL.append((params.wordConnect).join(refinedMorph))
								#tokOutL.append((params.wordConnect).join([x.split("=")[1] for x in token.morph.split("|") if x.split("=")[0] in params.morphs]))
						if params.morphsExtra != None: #added in v .57 on 2026-03-09
							if token.morph not in [None,""," "]:
								morph_list = []
								morphs = str(tag_string).split("|") #split the morphology output into a list
								morphDict = {}
								for x in morphs:
									item = x.split("=")
									morphDict[item[0]] = item[1]
								for d in morphsExtra:
									if d["key"] in morphDict and morphDict[d["key"]] == d["value"]:
										for m in d["morphs"]:
											if m in morphDict:
												morph_list.append(morphDict[m])
								
								refinedMorph = [x for x in morph_list if x not in [""]]
								if len(refinedMorph) >= 1:
									tokOutL.append((params.wordConnect).join(refinedMorph))

						if token.cwfw != None and params.includeCwFw == True:
							tokOutL.append(token.cwfw)
						if len(tokOutL) == 1:
							token.tokOut = tokOutL[0]
						if len(tokOutL) > 1:
							token.tokOut = (params.wordConnect).join(tokOutL)
					toks.append(token)
				sents.append(toks)
			normalized.append(sents)
		return(normalized)

	def normalize(self,fl_paras, params): #presumes a list with three levels [para[sent[token]]]
		normalized = []
		ignored = []
		for paras in fl_paras:
			sents = []
			for sent in paras:
				toks = []
				for token in sent:
					if token.tokOut != None:
						toks.append(token.tokOut)
					else:
						ignored.append("+".join([token.text,"_".join(token.preIgnoreReasons)]))
				sents.append(toks)
			normalized.append(sents)
		return(normalized,ignored)

	def ngramize(self,fl_paras, params,n=2): #presumes a list with three levels [para[sent[token]]]
		normalized = []
		ignored = []
		for paras in fl_paras:
			sents = []
			for sent in paras:
				ngrams = []
				#cleanSent = [x for x in sent if x.upos not in ["PUNCT"]]
				for idx, token in enumerate(sent):
					preNgram = [x.tokOut for x in sent[idx:idx+n]]
					if len(preNgram) < n:
						continue
					elif None in preNgram:
						ignored.append(preNgram)
						continue
					else:
						token.bgOut = params.ngramConnect.join(preNgram)
						ngrams.append(params.ngramConnect.join(preNgram))
				sents.append(ngrams)
			normalized.append(sents)
		return(normalized,ignored)

	def depBigrams(self,fl_paras, params): #presumes a list with three levels [para[sent[token]]]
		normalized = []
		ignored = []
		for paras in fl_paras:
			sents = []
			for sent in paras:
				depGrams = []
				#cleanSent = [x for x in sent if x.upos not in ["PUNCT"]]
				for token in sent:
					if token.deprel in params.deprels:
						if params.depOrder == "dep2head":
							preDep = [token.deprel,token.tokOut,sent[token.idxHead].tokOut]
						else:
							if token.idx < idxDict[token.idxCharHead]:
								preDep = [token.deprel,token.tokOut,sent[token.idxHead].tokOut]
							else:
								preDep = [token.deprel,sent[token.idxHead].tokOut,token.tokOut]
						if None in preDep:
							ignored.append(preDep)
							continue
						token.depbgOut = params.ngramConnect.join(preDep)
						depGrams.append(params.ngramConnect.join(preDep))
				sents.append(depGrams)
			normalized.append(sents)
		return(normalized,ignored)

	def paratok2text(self, paratok):
		texttoks = []
		for paras in paratok: #iterate through paragraphs
			para = []
			for sent in paras:
				para.append([tok.text for tok in sent])
			texttoks.append(para)
		return(texttoks)
	
	def para2sent(self,paratok):
		senttoks = []
		for paras in paratok: #iterate through paragraphs
			for sent in paras:
				senttoks.append(sent)
		return(senttoks)
	
	def senttok2text(self,senttok):
		senttext = []
		for sent in senttok:
			senttext.append([tok.text for tok in sent])
		return(senttext)
	
	def sent2tok(self,senttok):
		return([y for x in senttok for y in x])
	
	def tok2text(self,toks):
		return([x.text for x in toks])
		
	def __init__ (self, textObj = None, params = None): #this presumes a text object from preProcess
		#print(param.abbrvs)
		if textObj == None:
			self.paras = None
			self.sents = None
			self.toks = None
			self.paratxt = None
			self.senttxt = None
			self.toktxt = None
		else:
			#self.tokens = self.text2tok(text) #tokenized data
			self.parasto = self.tokProcess(textObj.parasto,params) #TokObject tokens ([[[]]]) [para[sent[tok]]]
			self.sentsto = self.para2sent(self.parasto) #TokObject tokens ([[]]) [sent[tok]]
			self.toksto = self.sent2tok(self.sentsto) #TokObject tokens ([]) [tok]
			self.normout = self.normalize(self.parasto,params)
			self.paras = self.normout[0] #normed paragraphs
			self.sents = self.para2sent(self.paras) #normed sentences
			self.toks = self.sent2tok(self.sents) #normed tokens
			self.ignored = self.normout[1]
			self.bgout = self.ngramize(self.parasto,params, 2) #default to bigrams
			self.paras_bg = self.bgout[0] #normed paragraphs
			self.sents_bg = self.para2sent(self.paras_bg) #normed sentences
			self.toks_bg = self.sent2tok(self.sents_bg) #normed tokens
			self.ignored_bg = self.bgout[1]
			# self.tgout = self.ngramize(self.parasto,params, 3) #default to trigrams
			# self.paras_tg = self.tgout[0] #normed paragraphs
			# self.sents_tg = self.para2sent(self.paras_tg) #normed sentences
			# self.toks_tg = self.sent2tok(self.sents_tg) #normed tokens
			# self.ignored_tg = self.tgout[1]
			self.depout = self.depBigrams(self.parasto,params) #default to bigrams
			self.paras_dep = self.depout[0] #normed paragraphs
			self.sents_dep = self.para2sent(self.paras_dep) #normed sentences
			self.toks_dep = self.sent2tok(self.sents_dep) #normed tokens
			self.ignored_dep = self.depout[1]


def corpus2Conllu(sourceFiles,targetLoc,params, suffList = [".txt"],verbose = True,nsamples = None,ignoreExt = False): #simple params
	fileList = []
	ignoreList = glob.glob(targetLoc + "*" + ".conllu")
	for suff in suffList:
		fileList = fileList + glob.glob(sourceFiles + "*" + suff)
	if nsamples != None:
		fileList = fileList[:nsamples]
	for fname in fileList:
		fname = Path(fname)
		fnameSimple = fname.name
		#fnameSimple = fname.split("/")[-1]
		newName = Path(targetLoc / fnameSimple + ".conllu")
		#newName = targetLoc + fnameSimple + ".conllu"
		if ignoreExt == True:
			if newName in ignoreList:
				print("Skipping", fnameSimple)
				continue
		if verbose == True:
			print(fnameSimple)
		tFile = open(fname,errors = "ignore", encoding="utf-8").read()
		#print(tFile[:100])
		processedFile = preProcess(tFile, params, encoding="utf-8")
		outSents = []
		for para in processedFile.parasto:
			for sent in para:
				outsent = []
				for token in sent:
					outTok = [token.idx,token.text,token.lemma,token.upos,token.xpos,token.morph,token.idxHead,token.deprel,"_","_"]
					outsent.append("\t".join([str(x) for x in outTok]))
				outSents.append("\n".join(outsent))
		outf = open(newName,"w", encoding="utf-8")
		outf.write("\n\n".join(outSents))
		outf.flush()
		outf.close()

def cc100corpus2Conllu(xzName,targetDir, params, batchSize = 100,total_batches = 500000): #simple params
	batch_sents = []
	n_batches = 0
	with lzma.open(xzName, mode='rt', encoding='utf-8') as file:
		for line in file:
	# big_file = open(x,"rb")
			batch_sents.append(line)
			if len(batch_sents) == batchSize:

		#print(tFile[:100])
				processedFile = lats.preProcess("".join(batch_sents), params)
				outSents = []
				for para in processedFile.parasto:
					for sent in para:
						outsent = []
						for token in sent:
							outTok = [token.idx,token.text,token.lemma,token.upos,token.xpos,token.morph,token.idxHead,token.deprel,"_","_"]
							outsent.append("\t".join([str(x) for x in outTok]))
						outSents.append("\n".join(outsent))
				
				with open(targetDir + "frcc100_" + str(n_batches) + ".conllu","w", encoding="utf-8") as outf:
					outf.write("\n\n".join(outSents))
				
				batch_sents = []
				n_batches += 1
				if int(n_batches/1000) == n_batches/1000:
					print(n_batches)
				if n_batches == total_batches:
					break
	print("Converted",str(n_batches), "texts")

class freqConllu(): #added 2025-03-18
	def freq_add(self,d,item):
		if item not in d:
			d[item] = 1
		else:
			d[item] += 1
	def frequency(self,fnames,params):
		tokd = {}
		bgd = {}
		depd = {}
		ignoredtoksd = {}
		nfiles = len(fnames)
		small_counter = 0
		big_counter = 0
		for fname in fnames:
			if small_counter == 100:
				print(big_counter,"of",nfiles,"processed")
				small_counter = 0
			small_counter +=1
			big_counter+=1
			#print(fname.split("/")[-1])
			conlluToks = preProcessConllu(open(fname).read())
			conlluNormalized = Normalize(conlluToks,params)
			for token in conlluNormalized.toks:
				self.freq_add(tokd,token)
			for ign in conlluNormalized.ignored:
				self.freq_add(ignoredtoksd,ign)
			for bg in conlluNormalized.toks_bg:
				self.freq_add(bgd,bg)
			for deps in conlluNormalized.toks_dep:
				self.freq_add(depd,deps)
		return([tokd,bgd,depd,ignoredtoksd])

	def __init__ (self, lof = None, params = None, suff = ".conllu"):
		
		if lof == None:
			self.tokfreqd = None
			self.bgfreqd = None
			self.depfreqd = None
			self.ignoredtokd = None

		else:
			self.freqout = self.frequency(lof,params)
			self.tokfreqd = self.freqout[0]
			self.bgfreqd = self.freqout[1]
			self.depfreqd = self.freqout[2]
			self.ignoredtokd = self.freqout[3]

def safe_divide(num,denom):
	if denom == 0:
		val = 0
	else:
		val = num/denom
	return(val)

def dictLU(token,dictionary,subKey): #dict look up
	if subKey == None:
		if token in dictionary:
			val = dictionary[token]
		else:
			val = None
	else:
		if token in dictionary[subKey] and dictionary[subKey][token] != "n/a":
			val = dictionary[subKey][token]
		else:
			val = None
	return(val)

def indexer(indexDict,preProcessed): #this version is token-centric instead of index-centric #list of index classes, token_object list
	textd = {} #text level dictionary
	for normType in indexDict: #deal with one norming type at a time
		normedText = Normalize(preProcessed,normType["norming"])
		for token in normedText.toksto: #iterate through token objects
			for index in normType["indices"]: #for each token object, get index value
				val = None
				indexn = "_".join([x for x in [index.basen, index.word_form,index.tokenType,index.dictKey,index.transformation]if x not in [None]])
				if indexn not in textd:
					textd[indexn] = {"valList" : [], "val" : None, "coverageList" : [], "tokList": [], "diagnList" : []} #to hold list of values for eventual visualization
				if index.tokenType in ["aw","cw","fw"]:
					diagTok = token.tokOut
					if index.tokenType == "aw":
						normTok = token.tokOut
					else:
						if token.cwfw == index.tokenType:
							normTok = token.tokOut
						else:
							normTok = None
				elif index.tokenType == "bg":
					diagTok = token.bgOut
					normTok = token.bgOut
				elif index.tokenType == "depbg":
					diagTok = token.depbgOut
					normTok = token.depbgOut
				else:
					diagTok = None
					normTok = None #may need to add error handling here
				if index.indexType in ["meanScore"]:
					if normTok != None:
						rawValue = dictLU(normTok,index.dictionary,index.dictKey) #tokenType, target dictionary, sub key
						if rawValue == None:
							textd[indexn]["coverageList"].append(0) #add to coverage list
						elif index.minval != None and rawValue < index.minval:
							textd[indexn]["coverageList"].append(0) #add to coverage list
						else:
							if index.transformation not in ["log10","logn","pm"]:
								val = rawValue
							if index.transformation == "log10":
								val = math.log10(rawValue) #log base 10
							if index.transformation == "logn":
								val = math.log(rawValue) #log natural
							if index.transformation == "pm":
								val = (rawValue/corp_size) * 1000000 #per million
							#tokenD[indexn] = val
							textd[indexn]["valList"].append(val) # add to val_list
							textd[indexn]["coverageList"].append(1) #add to coverage list
					
					#textd[indexn]["diagnList"].append({"Item" : token.text,"diagTok" :diagTok,"normTok":normTok,"val" : val})
				else:
					if normTok != None:
						val = "ld"
				if normTok != None:
					textd[indexn]["tokList"].append(normTok)
				textd[indexn]["diagnList"].append({"Item" : token.text,"diagTok" :diagTok,"normTok":normTok,"val" : val})
		
		
		for index in normType["indices"]: #for each token object, get index value
			indexn = "_".join([x for x in [index.basen, index.word_form,index.tokenType,index.dictKey,index.transformation] if x not in [None]])
			if index.indexType == "meanScore":
				#calculate mean score
				textd[indexn]["val"] = safe_divide(sum(textd[indexn]["valList"]),len(textd[indexn]["valList"]))
			if index.indexType == "ld":
				ldv = ld()
				if index.ldType == "mattr":
					textd[indexn]["val"] = ldv.MATTR(textd[indexn]["tokList"],index.varVal,True)[0]
				if index.ldType == "mtld":
					textd[indexn]["val"] = ldv.MTLD(textd[indexn]["tokList"],ttrval = index.varVal,outputs = False)

	return(textd)

### add SOA code
def freq_add(freqD,item,cmbItem,cmbFreqD):
	if item not in freqD:
		freqD[item] = cmbFreqD[cmbItem]
	else:
		freqD[item] += cmbFreqD[cmbItem]

def soa(item1FreqDict,item2FreqDict,combinedFreqDict,cut_off = 5,deprel = [None], splitter = "__"): #need to finish this
	if item1FreqDict == None and item2FreqDict == None :#for dependency SOA
		item1FreqDict = {}
		item2FreqDict = {}
		for item in combinedFreqDict:
			itemParts = item.split(splitter)
			itemRel = itemParts[0]
			#print(itemRel)
			if itemRel in deprel:
				item1 = itemParts[1]
				item2 = itemParts[2]
				freq_add(item1FreqDict,item1,item,combinedFreqDict)
				freq_add(item2FreqDict,item2,item,combinedFreqDict)

				### finish this! ###
	#print(len(item1FreqDict))
	mi = {}
	tscore = {}
	faith_item1_cue = {}
	faith_item2_cue = {}
	deltap_item1_cue = {}
	deltap_item2_cue = {}

	corpus_size = sum(item1FreqDict.values()) #number of items in corpus
	#target_freq = sum(freq_dict["target_freq"].values()) #not sure what this is for need to double check

	#need to figure out how to do SOA with dep bigrams
	for combination in combinedFreqDict:
		if deprel == [None]:
			if len(combination.split(splitter)) > 2: #ignore problematic cases
				continue
			item1 = combination.split(splitter)[0] #get lemma from combination
			item2 = combination.split(splitter)[1]
		else:
			if combination.split(splitter)[0] not in deprel:
				continue
			else:
				item1 = combination.split(splitter)[1] #get lemma from combination
				item2 = combination.split(splitter)[2]

		#print(combination)

		#print(lemma)
		observed = combinedFreqDict[combination] #this is the combination frequency
		item1Freq = item1FreqDict[item1] #e.g., word one
		item2Freq = item2FreqDict[item2] #e.g., word two
		#print(combination)
		if combinedFreqDict[combination] >= cut_off: #cut_off here is corpus frequency cutoff - default is 5
			#print(type(lemmaFreq),type(observed),type(structureFreq),type(corpus_size))
			expected = ((item1Freq * item2Freq)/corpus_size)
			#print(expected)
			mi[combination] =  math.log2(observed/expected) #this should be good
			#print(mi[combination])
			tscore[combination] = (observed-expected)/(math.sqrt(observed))
			#print(tscore[combination])
			a = observed
			b = item1Freq - a #collocate
			c = item2Freq - a #target
			d = corpus_size - (a+b+c)
			#start here
			faith_item1_cue[combination] = (a/(a+b))
			faith_item2_cue[combination] = (a/(a+c))

			deltap_item1_cue[combination] = (a/(a+b)) - (c/(c+d))
			deltap_item2_cue[combination] = (a/(a+c)) - (b/(b+d))

			#start here

	output_dict = {"mi" : mi,"tscore" : tscore, "faith_item1_cue" : faith_item1_cue, "faith_item2_cue" : faith_item2_cue, "deltap_item1_cue" : deltap_item1_cue, "deltap_item2_cue" : deltap_item2_cue}
	return(output_dict)

def multiIndexer(loFnames,indexDict,baseParams): 
	outd = {}
	for fname in loFnames:
		fname = Path(fname)
		simpleName = fname.name
		#simpleName = fname.split("/")[-1]
		print("processing:",simpleName)
		tokObj = preProcess(open(fname,errors="ignore", encoding="utf-8").read(), params = baseParams)

		outd[simpleName] = indexer(indexDict,tokObj)
	return(outd)

def indexWriter(indexDict,outname): #for writing indices to a spreadsheet
	header = []
	headerDone = False
	for fname in indexDict: #deal with automatically generating header
		if headerDone == True:
			break
		else:
			for index in indexDict[fname]:
				header.append(index)
			headerDone = True
	outList = []
	outList.append("\t".join(["fname"]+header))
	for fname in indexDict:
		flist = [fname]
		for index in header:
			flist.append(str(indexDict[fname][index]["val"]))
		outList.append("\t".join(flist))
	outf = open(outname,"w", encoding="utf-8")
	outf.write("\n".join(outList))
	outf.flush()
	outf.close()
	print("Wrote output to",outname)

def diagWriter(indexDict,outDir): #for writing diagnostic files
	orderList = ["Item","diagTok","normTok","val"]
	for fname in indexDict:
		bigOutList = []
		for index in indexDict[fname]:
			outList = [index,"\t".join(orderList)]
			for token in indexDict[fname][index]["diagnList"]:
				tokenL = []
				for x in orderList:
					tokenL.append(token[x])
				outList.append("\t".join([str(x) for x in tokenL]))
			bigOutList.append("\n".join(outList))
		outf = open(Path(outDir+fname+"_diagnostic.txt"),"w", encoding="utf-8")
		outf.write("\n\n".join(bigOutList))
		outf.flush()
		outf.close()

### Anything below here still needs to be tested/updated ###

### In Progress Code ###





#this = {"mytext.txt" : "This is my text"}
# def multiIndexer(lotob,indices): #list of [(filename,text_object)] text files (or filenames), list of indices, whether list is filenames or not (default is True)
# 	outd = {}
# 	for simpleName, textObj in lotob:
# 		outd[simpleName] = indexer(indices,textObj)
# 	return(outd)

#### Parallel Analysis
class parallel():
	def sampler(self, tok_text, mn = 50, mx = 200, interval = 5): #(tokenized text, minimum text lenth,maximum text length, text length interval)
		#too_short = False
		sample_dict = {}
	
		iterations  = int((mx - mn)/interval)+1 #number of lengths to examine.
		#print(iterations)
	
		if len(tok_text) < mx:
			print("Warning: Text is too short")
			#too_short = True
		else:
			start = mn
			#print(start)
			tok_text = tok_text[:mx]
		
			for x in range(iterations):
				sample_list = []
				n_samples = int(mx/start)
				#print(n_samples)
			
				for y in range(n_samples):
					sample_list.append(tok_text[((y)*start):((y+1)*start)])
				
				sample_dict[start] = sample_list
				start+=interval
			
	
		return(sample_dict)
	
	def analysis(self,tok_text,funct, mn = 50, mx = 200, interval = 5): #tokenized text, analysis function,minimum,maximum,interval
		sampled = self.sampler(tok_text,mn,mx,interval)
		vald = {}
		for tl in sampled: #iterate through text lengths
			vald[tl] = {"val" : None, "vals" : []}
			for text in sampled[tl]: #iterate through texts
				vald[tl]["vals"].append(funct(text)) #append item values
			vald[tl]["val"] = stat.mean(vald[tl]["vals"]) #calculate mean scores
		
		return(vald)
	
	def analyses(self,tok_text,functd, mn = 50, mx = 200, interval = 5): #functd is a {"FunctionName":function} dictionary
		sampled = self.sampler(tok_text,mn,mx,interval)
		outd = {}
		for name in functd:
			outd[name] = self.analysis(tok_text,functd[name], mn, mx, interval)
	
		return(outd) #{"FunctionName" : {"Length" : {"val" : average_value, "vals" : [all values]}}}

	def __init__(self, text = None, funct = None, functd = None,mn = 50,mx = 200,interval = 5):
		if text != None:
			#self.text = text
			self.samples = self.sampler(text,mn,mx,interval)
			if functd != None:
				self.valsd = self.analyses(text,functd,mn,mx,interval)
			if functd == None and funct!= None:
				self.vald = self.analysis(text,funct,mn,mx,interval)

class Frequency():
	def freq_add(self,d,item):
		if item not in d:
			d[item] = 1
		else:
			d[item] += 1

	def corp_freq(self, lof,params,fnm = True,types = ["token","bigram","ignored"]): #lof = list of files. If fnm == True, then the list includes filenames. Otherwise, it includes strings
		outd = {} #frequency dict
		for x in types:
			outd[x] = {}
		for text in lof:
			if fnm == True:
				text = open(text, encoding = "utf-8", errors = "ignore")
			normed = Normalize(text,params)
			for x in types:
				if x == "token":
					for tok in normed.toks:
						self.freq_add(outd["token"],tok)
				if x == "bigram":
					for bg in normed.toks_bg:
						self.freq_add(outd["bigram"],bg)
				if x == "ignored":
					for ign in normed.ignored:
						self.freq_add(outd["ignored"],"\t".join(ign))
		return(outd)

	def __init__ (self, lof = None, fnm = False, types = ["token","bigram","ignored"], params = None):
		
		if lof == None:
			self.freqd = None
			self.tokfreq = None
			self.bgfreq = None
			self.tokfreqd = None
			self.bgfreqd = None
			self.ignored = None

		else:
			self.freqd = self.corp_freq(lof,params,fnm)
			if "token" in self.freqd:
				self.tokfreqd = self.freqd["token"]
				self.tokfreq = sorted(self.tokfreqd.items(), key = itemgetter(1),reverse = True)
			else:
				self.tokfreqd = None
			if "bigram" in self.freqd:
				self.bgfreqd = self.freqd["bigram"]
				self.bgfreq = sorted(self.bgfreqd.items(), key = itemgetter(1),reverse = True)
			else:
				self.bgfreqd = None
			if "ignored" in self.freqd:
				self.ignoredd = self.freqd["ignored"]
				self.ignored = sorted(self.ignoredd.items(), key = itemgetter(1),reverse = True)

def multiLoad(lotf,parameters,fnm = True,verbose = True,big_count = 20): #list of text files (or filenames), list of indices, whether list is filenames or not (default is True)
	outl = []
	total_num = len(lotf)
	minicount = 0 #for user output
	if verbose == True:
		print("Pylats is preprocessing", total_num,"files")
	for idx,textn in enumerate(lotf):
		if fnm == True:
			text = open(textn, encoding = "utf-8", errors = "ignore").read()
			simpleName = textn.split("/")[-1] #last item in filepath
		elif isinstance(textn,tuple) == True: #can use (filename,text) tuples
			simpleName = textn[0]
			text = textn[1]
		else:
			simpleName = str(idx) #if a filename isn't provided, use the idx as the filename
		
		### progress for user ###
		if verbose == True:
			if total_num <=200:
				print("Processing",idx,"of",total_num,"files. Filename =",simpleName)
			else:
				if minicount == big_count:
					print("Processing",idx,"of",total_num,"files. Filename =",simpleName)
					minicount = 0
				else:
					minicount += 1
		###########################

		normed = Normalize(text,parameters)
		outl.append((simpleName,normed))
	return(outl)

# def indexWriter(valdict,index_list,outname = "results.csv",sep = "\t",target = "value"):
# 	outf = open(outname,"w",encoding = "utf-8")
# 	header_list = ["filename"] + index_list
# 	outf.write(sep.join(header_list))
# 	for fnm in valdict:
# 		outlist = [fnm] + [str(valdict[fnm][x][target]) for x in index_list]
# 		outf.write("\n" + sep.join(outlist))
# 	outf.flush()
# 	outf.close()

def exampleWriter(valdict,index_list,outdir = "itemOutput/",sep = "\t"):
	os.mkdir(outdir) #may want to add datetime here in the future to avoid overwriting
	header_list = ["raw","lowered","lemma","UPOS","XPOS","basic_bigram"] + index_list
	for fnm in valdict:
		outf = open(outdir+fnm,"w",encoding = "utf-8") #may want to change this name further
		outf.write(sep.join(header_list))
		for token in valdict[fnm]["tokensList"]:
			outlOne = [token["tokobj"].text,token["tokobj"].text.lower(),token["tokobj"].lemma_, token["tokobj"].pos_, token["tokobj"].tag_,token["bg"]]
			outltwo = [token[x] for x in index_list]
			outl = outlOne + outltwo
			outl = [str(x) for x in outl]
			outf.write("\n" + sep.join(outl))
	outf.flush()
	outf.close()

def frPostHocAdjust(token,sent):
	if token.lemma_ in ["pouvoir"] and token.deprel in ["advmod"]:
		if sent[token.idx+1].text in ["-"] and sent[token.idx+1].deprel in ["advmod"]:
			if sent[token.idx+2].lemma_ in ["être"] and sent[token.idx+1].deprel in ["advmod"]:
				print("OK")
				#finish this, result should be = "peut-être_ADV" 


#samples:
textsmpl = """When you will go sutdy in any moment you has time for choose the subject that you want start o study. Becuase is important know that you want study and that subject you will study. I disagree whit it is more importnat to choose to study subjects that me more want than to choose subject to prepare foir  a job or career.

First of all, when you enter to University, no answer that shubject you want or like study. The subject just was and you has begin when they said. In this moment you does not choose that like subject you want. Only you choose what career wants study. While if you will arrive at university and they said that you has choose subject, may be you choose some that no are important for you job or are not intereste by you career.

On the other hand, in my opinion is important kwon subject about of my work or my career, since if you choose that you like, you can get good results in your work and can be has problems with you managers. For example: you studied business adminitration and when you was in the university  you studied subject about of chemestry, this not will help made business becuase this subject is for teach different elements that there are in the chemestry.

In conclusion is importsnt study subject that are imporntant for your career or you job. In some cases no will like the subject but you has has fource for take """





