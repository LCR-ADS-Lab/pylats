#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 10:35:53 2021

@author: kristopherkyle

"""
version = ".33"
#need to test numbers.
import math
import os
import pickle
from operator import itemgetter
import statistics as stat
from collections import Counter
import pkg_resources #for importing data from packages
from os.path import exists

#still need to deal with real words list (because we will have multiple)

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

en_rwl = pickle.load(open(get_fname('pylats',"real_words5.pickle"),"rb")) #words in written COCA that occur at least 5 times
en_10kpos = pickle.load(open(get_fname('pylats',"10k_pos_noes.pickle"),"rb")) #words in written COCA that occur at least 5 times#words in COCA that are within the most frequent 10k
en_10kraw = pickle.load(open(get_fname('pylats',"10k_raw_noes.pickle"),"rb")) #words in written COCA that occur at least 5 times#words in COCA that are within the most frequent 10k
cedel_ignore = pickle.load(open(get_fname('pylats',"cedel_ignore.pickle"),"rb")) #words in written COCA that occur at least 5 times#words in COCA that are within the most frequent 10k



statusd = {"spld":False,"mdld":False,"models" : []} #for updating and maintaining load statuses

def load_model(modelname): # this is an attempt to get a module to load easily
	print("Attempting to load spacy model:", modelname)
	if statusd["spld"] == True: #if spacy has been successfully loaded
		try:
			nlp = spacy.load(modelname) #try to load model
			statusd["mdld"] = True #set dictionary value
			statusd["models"].append(modelname) #set dictionary value
			print("Successfully loaded spacy model:",modelname)
		except OSError:
			print("The selected model <",modelname,"> does not seem to be available on your system.\nPlease load a different model or see Spacy documentation for assistance.")
	else:
		print("You cannot load a Spacy model because pylats was not able to import Spacy. This most likely means that Spacy is not installed on your system.")
	if statusd["mdld"] == False:
		nlp = None
	return(nlp)

try: 
	import spacy
	statusd["spld"] = True
except ModuleNotFoundError:
	print("Spacy has not been installed.\nTo access pylats advanced features for English or Spanish, please install Spacy.")
	statusd["spld"] = False

# if statusd["spld"] == True:
# 	try:
# 		nlp_en_sm = spacy.load("en_core_web_sm")
# 		statusd["models"].append("en_core_web_sm")
# 	except OSError:
# 		print("The selected model <",modelname,"> does not seem to be available on your system.\nPlease load a different model or see Spacy documentation for assistance.")
# 		if statusd["mdld"] == False:
# 			statusd["mdld"] = False

nlp_en_sm = load_model("en_core_web_sm")
nlp_en_trf = load_model("en_core_web_trf")
nlp_es_sm = load_model("es_core_news_sm")
nlp_es_trf = load_model("es_dep_news_trf")

#default parameters
class parameters: #default English parameters
	lang = "en"
	model = "en_core_web_sm"
	try:
		nlp = nlp_en_sm
	except NameError:
		nlp = None
	punctuation = ['``', "''", "'", '.', ',', '?', '!', ')', '(', '%', '/', '-', '_', '-LRB-', '-RRB-', 'SYM', ':', ';', '"']
	punctse = [".","?","!"]
	abbrvs = ["mrs.","ms.","mr.","dr.","phd."]
	splitter = "\n" #for splitting paragraphs
	rwl = en_rwl
	sp = True
	sspl = "spacy"
	pos = None #other options are "pos" for Penn tags and "upos" for universal tags
	removel = ['becuase'] #typos and other words not caught by the real words list
	lemma = False
	lower = True #treat all words as lower case
	attested = False #filter output using real words list?
	spaces = [" ","  ","   ","    "] #need to add more here
	override = [] #items the system ignores that should be overridden
	posignore = []
	numbers = ["NUM"] #pos_ tag for numbers
	nonumbers = True
	connect = "__" #for connecting ngrams
	contentPOS = [] #can be added, blank for now
	contentLemIgnore = [] #can be added, blank for now

#other parameters:
class ld_params_en:
	lang = "en"
	model = "en_core_web_sm"
	try:
		nlp = nlp_en_sm
	except NameError:
		nlp = None
	punctuation = ['``', "''", "'", '.', ',', '?', '!', ')', '(', '%', '/', '-', '_', '-LRB-', '-RRB-', 'SYM', ':', ';', '"']
	punctse = [".","?","!"]
	abbrvs = ["mrs.","ms.","mr.","dr.","phd."]
	splitter = "\n" #for splitting paragraphs
	rwl = en_rwl
	sp = True
	sspl = "spacy"
	pos = "upos" #other options are "pos" for Penn tags and "upos" for universal tags
	removel = ['becuase'] #typos and other words not caught by the real words list
	lemma = True
	lower = True #treat all words as lower case
	attested = True #filter output using real words list?
	spaces = [" ","  ","   ","    "] #need to add more here
	override = [] #items the system ignores that should be overridden
	posignore = []
	numbers = ["NUM"] #pos_ tag for numbers
	nonumbers = True
	connect = "__" #for connecting ngrams
	contentPOS = [] #can be added, blank for now
	contentLemIgnore = [] #can be added, blank for now

class ld_params_en_trf:
	lang = "en"
	model = "en_core_web_trf"
	try:
		nlp = nlp_en_trf
	except NameError:
		nlp = None
	punctuation = ['``', "''", "'", '.', ',', '?', '!', ')', '(', '%', '/', '-', '_', '-LRB-', '-RRB-', 'SYM', ':', ';', '"']
	punctse = [".","?","!"]
	abbrvs = ["mrs.","ms.","mr.","dr.","phd."]
	splitter = "\n" #for splitting paragraphs
	rwl = en_rwl
	sp = True
	sspl = "spacy"
	pos = "upos" #other options are "pos" for Penn tags and "upos" for universal tags
	removel = ['becuase'] #typos and other words not caught by the real words list
	lemma = True
	lower = True #treat all words as lower case
	attested = True #filter output using real words list?
	spaces = [" ","  ","   ","    "] #need to add more here
	override = [] #items the system ignores that should be overridden
	posignore = []
	numbers = ["NUM"] #pos_ tag for numbers
	nonumbers = True
	connect = "__" #for connecting ngrams
	contentPOS = [] #can be added, blank for now
	contentLemIgnore = [] #can be added, blank for now


class parameters_es: #these are for the Spanish parameters - these need to be updated
	lang = "es"
	model = "es_core_news_sm" #also es_dep_news_trf
	try:
		nlp = nlp_es_sm
	except NameError:
		nlp = None
	punctuation = ['``', "''", "'", '.', ',', '?', '!', ')', '(', '%', '/', '-', '_', '-LRB-', '-RRB-', 'SYM', ':', ';', '"','¿','¡','”','“','…',"--","–","»","]","["]
	punctse = [".","?","!"]
	abbrvs = [] #these can be added
	splitter = "\n" #for splitting paragraphs
	rwl = [] #this will need to be updated
	sp = True
	sspl = "spacy"
	pos = None #other options are "pos" for fine-grained tags and "upos" for universal tags
	removel = en_10kraw + en_10kpos + cedel_ignore #typos and other words not caught by the real words list also, frequent English words that may occur in L2 corpora may need to filter these
	lemma = False
	lower = True #treat all words as lower case
	attested = False #filter output using real words list?
	spaces = [" ","  ","   ","    "]  #need to add more here
	override = [] 
	posignore = ["PROPN"] #proper nouns and numbers. Note that some numbers are missed. Need to fix.
	numbers = ["NUM"] #pos_ tag for numbers
	nonumbers = True
	connect = "__" #for connecting ngrams
	contentPOS = ["VERB","NOUN","PROPN","ADJ","ADV"] #note that PROPN will be overridden by posignore in this case
	contentLemIgnore = ["ser","estar"] #note that these are actually already ignored because they are tagged as "AUX"

class parameters_es_trf: #these are for the Spanish parameters - these need to be updated
	lang = "es"
	model = "es_dep_news_trf" #also es_dep_news_trf
	try:
		nlp = nlp_es_trf
	except NameError:
		nlp = None
	punctuation = ['``', "''", "'", '.', ',', '?', '!', ')', '(', '%', '/', '-', '_', '-LRB-', '-RRB-', 'SYM', ':', ';', '"','¿','¡','”','“','…',"--","–","»","]","["]
	punctse = [".","?","!"]
	abbrvs = [] #these can be added
	splitter = "\n" #for splitting paragraphs
	rwl = [] #this will need to be updated
	sp = True
	sspl = "spacy"
	pos = None #other options are "pos" for fine-grained tags and "upos" for universal tags
	removel = en_10kraw + en_10kpos + cedel_ignore #typos and other words not caught by the real words list also, frequent English words that may occur in L2 corpora may need to filter these
	lemma = False
	lower = True #treat all words as lower case
	attested = False #filter output using real words list?
	spaces = [" ","  ","   ","    "]  #need to add more here
	override = [] 
	posignore = ["PROPN"] #proper nouns and numbers. Note that some numbers are missed. Need to fix.
	numbers = ["NUM"] #pos_ tag for numbers
	nonumbers = True
	connect = "__" #for connecting ngrams
	contentPOS = ["VERB","NOUN","PROPN","ADJ","ADV"] #note that PROPN will be overridden by posignore in this case
	contentLemIgnore = ["ser","estar"] #note that these are actually already ignored because they are tagged as "AUX"

class TokObject(): #need to add
	def spacy_morph(self, tag_string,ud_tag):
		if ud_tag in ["AUX","VERB"]:
			morph_list = []
			morphs = str(tag_string).split("|") #slit the morphology output into a list
			for x in morphs: #iterate through the morpheme information
				#print(x)
				if "Mood" in x: #This will be Indicative or Subjunctive (I think), 
					#print(x)
					morph_list.append(x.split("=")[-1])
				if "Tense" in x: #this includes aspect - present, past, perfect, etc.
					morph_list.append(x.split("=")[-1])
				
				if len(morph_list) == 0 and "VerbForm" in x: #this is to mark infinitives
					morph_list.append(x.split("=")[-1])
			
			if len(morph_list) > 0: 
				return(ud_tag + "_" + "_".join(morph_list))
			else:
				return(ud_tag)
		else:
			return(ud_tag)
	def num_check(self,item):
		num = False
		for x in [0,1,2,3,4,5,6,7,8,9]:
			if str(x) in item:
				num = True
		return(num)

	def __init__(self, token = None,counter = 0, params = parameters): #see parameters object for all relevant variables
		self.idx = counter #position in sentence
		self.preIgnore = False #This will be the preprocessing ignore indicator
		self.preIgnoreReasons = []
		self.indexIgnore = False #This will be for exclusion based on database (or other constraints)
		if "spacy" in str(type(token)): #check for spacy token
			self.text = token.text #raw text
			self.lemma_ = token.lemma_ #raw text #lemma form (same as spacy)
			self.pos_ = token.pos_ #Universal pos tag (same as spacy)
			if params.lang == "es":
				self.tag_ = self.spacy_morph(token.morph,token.pos_) #special morphology tag for spanish verbs
			else:
				self.tag_ = token.tag_ #Specific POS tag (same as spacy)
			self.dep_ = token.dep_ #dependency relationship (same as spacy)
			self.head = token.head #head object (same as spacy)
			self.nchars = len(token.text) #length of item in chars
			#still need to deal with:
			if self.pos_ in params.contentPOS and self.lemma_.lower() not in params.contentLemIgnore:
				self.type = "cw" #content word
			else:
				self.type = "fw" #function word

		elif type(token) == str:
			self.text = token #raw text
			self.nchars = len(token) #length of item in chars
			self.lemma_ = None #lemma form (same as spacy)
			self.pos_ = None #Universal pos tag (same as spacy)
			self.tag_ = None #Specific POS tag (same as spacy)
			self.dep_ = None #dependency relationship (same as spacy)
			self.head = None #head object (same as spacy)
			self.type = None #function word, content word, or punctuation?

		else:
			print("Error: Expected spacy token or string, got", str(type(token)),"instead")
		self.attrs = {} #attributes can be added to this as needed
		#real words
		if self.text.lower() in params.rwl:
			self.isreal = True

		else: 
			self.isreal = False
			if params.attested == True:
				self.preIgnore = True #ignore due to not a real word
				self.preIgnoreReasons.append("Not in real word list")
		#punctuation
		if self.text in params.punctuation:
			self.ispunct = True
			self.preIgnore = True #ignore due to spaces
			self.preIgnoreReasons.append("Is punctuation")

		else:
			self.ispunct = False
		#spaces
		if self.text in params.spaces:
			self.isspace = True
			self.preIgnore = True #ignore due to spaces
			self.preIgnoreReasons.append("Is a space")
		else:
			self.isspace = False
		if self.num_check(self.text) == True or self.pos_ in params.numbers:
			self.isnumber = True
		else:
			self.isnumber = False
		#add normalize pieces here, add CW stuff here as well
		if self.text.lower() in params.override:
			self.override = True
		else:
			self.override = False
		if self.text in params.removel:
			self.inremove = True
			self.preIgnore = True
			self.preIgnoreReasons.append("In remove list")
		else:
			self.inremove = False
		if self.pos_ != None and self.pos_ in params.posignore:
			self.inposignore = True
			self.preIgnore = True #ignore due to POS
			self.preIgnoreReasons.append("Ignored POS")
		else:
			self.inposignore = False
		### This section focuses on ignoring words
		if params.nonumbers == True and self.isnumber == True:
			self.preIgnore = True #ignore because it is a number
			self.preIgnoreReasons.append("Numbers Ignored")

class Normalize: #working copy complete, still need to streamline functions; still needs to be debugged

	def text2tok(self,text, params = parameters): #punctuation defaults to the params class definition.
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
				tok_text.append(TokObject(token,counter,params))
				counter +=1
		else: #if sp == True, rely on Spacy for tokenization
			text = text.replace("\n"," ")
			for token in params.nlp(text):
				tok_text.append(TokObject(token,counter,params))#realwords relies on a global variable
				counter+=1
		return(tok_text)

	#sentence tokenize - simple, rule-based method for spliting a string into list of sentence strings. Presumes that words are split by whitespace and sentences are divided by "\n" or sentence -ending punctuation
	def text2sent(self, text, params = parameters):
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
	
	#paragraph tokenize - rule based method of splitting a string into paragraph strings. By default, presumes that paragraphs are separated by "\n"
	def text2para(self, text, params = parameters):
		paras = []
		for x in text.split(params.splitter):
			if len(x) == 0:
				continue
			else:
				paras.append(x)
		return(paras)
	
	#pipeline for sentences and tokens
	def text2toks(self, text, params = parameters): #sspl options include: spacy, simple - will add more in the future
		#punctse = params.punctse,punctuation = params.punctuation, realwords = params.rwl, sp = params.sp, sspl = params.sspl
		tok_texts = []
		if params.sp == True: #message if spacy is selected but not available
			if statusd["spld"] == False or statusd["mdld"] == False: #global variables that indicate whether spacy itself and a spacy model has been loaded
				print("Spacy processing selected, but either spacy and/or the spacy nlp model is not available. Defaulting to simple rule-based tokenization.")
				params.sp = False
				params.sspl = "simple" #this is not ideal in this case
		
		if params.sp == True:
			if params.sspl == "spacy":
				doc = params.nlp(text)
				for sent in doc.sents:
					toks = []
					counter = 0
					for token in sent:
						toks.append(TokObject(token, counter, params))#realwords relies on a global variable
						counter +=1
					tok_texts.append(toks)
			if params.sspl == "simple":
				for sent in self.text2sent(text, params):
					tok_texts.append(self.text2tok(sent,params))

		else:
			for sent in self.text2sent(text, params):
				tok_texts.append(self.text2tok(sent, params))
		return(tok_texts)
	
	#pipeline for paragraph, sentences, and tokens
	def text2tokp(self,text, params = parameters):
		tok_texts = []
		for para in self.text2para(text, params):
			tok_texts.append(self.text2toks(para, params))
		return(tok_texts)
	
	def tok2str(self,token,params = parameters): #format finalized string
		if params.lemma == True:
			outstr = token.lemma_
		else:
			outstr = token.text
		if params.lower == True:
			outstr = outstr.lower()

		if params.pos == None or statusd["spld"] == False or statusd["mdld"] == False: #if params say no pos or spacy isn't loaded:
			return(outstr)
		
		else:
			if params.pos == "pos":
				return("_".join([outstr,token.tag_]))
			elif params.pos == "upos":
				return("_".join([outstr,token.pos_]))
			else: #if something else was erroneously used as a keyword
				return(outstr)

	def normalize(self,fl_paras, params = parameters): #presumes a list with three levels [para[sent[token]]]
		normalized = []
		ignored = []
		for paras in fl_paras:
			sents = []
			for sent in paras:
				toks = []
				for tok in sent:
					#if item in override, then don't worry about other checks:
					if tok.override == True:
						toks.append(self.tok2str(tok,params))
						continue
					#otherwise:
					if tok.preIgnore == True:
						continue
					toks.append(self.tok2str(tok,params))
				sents.append(toks)
			normalized.append(sents)
		return(normalized,ignored)

	def ngramize(self,fl_paras, params = parameters,n=2): #presumes a list with three levels [para[sent[token]]]
		
		def ngrammer(tokenized,number,params): #create ngram list
			#step 1: clean text of unwanted punctuation and/or spaces
			cleaned = []
			for tok in tokenized:
				if tok.text in params.override: #if overriden, don't ignore
					cleaned.append(tok)
					continue
				elif tok.ispunct == True or tok.isspace == True:
					#ignored.append((tok.text,"(in punctuation list)"))
					continue
				else:
					cleaned.append(tok)
			#step 2: create ngram list
			ngram_list = [] #empty list for ngrams
			last_index = len(cleaned) #this will let us know what the last index number is
			for i , token in enumerate(cleaned): #enumerate allows us to get the index number for each iteration (this is i) and the item
				if i + number > last_index: #if the next index doesn't exist (because it is larger than the last index)
					continue
				else:
					ngram = cleaned[i:i+number] #the ngram will start at the current word, and continue until the nth word
					#ngram_string = connect.join(ngram) #turn list of words into an n-gram string
					ngram_list.append(ngram) #add ngram to ngram_list
			return(ngram_list) # return list of ngram token objects
			
		normalized = []
		ignored = []
		for paras in fl_paras:
			sents = []
			for sent in paras:
				ngramtoks = ngrammer(sent,n,params)
				ngrams = [] #for cleaned ngrams
				for ngram in ngramtoks:
					problem = False #for checking for issues in the ngrams
					for tok in ngram:
						#if item in override, then don't worry about other checks:
						if tok.text in params.override:
							# toks.append(self.tok2str(tok,params))
							continue
						if tok.text in params.removel:
							problem = True
							continue
						if params.nonumbers == True and tok.isnumber == True:
							ignored.append((self.tok2str(tok,params),"(is a number)"))
							continue
						if params.attested == True and tok.isreal == False:
							problem = True
							continue
						if tok.pos_ in params.posignore: #ignore certain parts of speech (such as proper nouns) - need to add this to the Normalize function
							problem = True
							continue

					ngram_tok = params.connect.join([self.tok2str(x,params) for x in ngram])
					#print(ngram_tok,problem)
					if problem == True:
						ignored.append(ngram_tok)
					else:
						ngrams.append(ngram_tok)
				sents.append(ngrams)
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
		
	def __init__ (self, text = None, params = parameters):
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
			self.paratxt = self.paratok2text(self.parasto) #Raw tokenized text tokens ([[[]]]) [para[sent[tok]]]
			self.senttxt = self.senttok2text(self.sentsto) #Raw tokenized text tokens ([[]]) [sent[tok]]
			self.toktxt = self.tok2text(self.toksto) #Raw tokenized text tokens ([]) [tok]
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

	def __init__ (self, lof = None, fnm = False, types = ["token","bigram","ignored"], params = parameters):
		
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
	for idx,text in enumerate(lotf):
		if fnm == True:
			text = open(text, encoding = "utf-8", errors = "ignore")
			simpleName = fnm.split("/")[-1] #last item in filepath
		elif isinstance(text,tuple) == True: #can use (filename,text) tuples
			simpleName = text[0]
			text = text[1]
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

def indexWriter(valdict,index_list,outname = "results.csv",sep = "\t",target = "value"):
	outf = open(outname,"w",encoding = "utf-8")
	header_list = ["filename"] + index_list
	outf.write(sep.join(header_list))
	for fnm in valdict:
		outlist = [fnm] + [str(valdict[fnm][x][target]) for x in index_list]
		outf.write("\n" + sep.join(outlist))
	outf.flush()
	outf.close()

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

#samples:
textsmpl = """When you will go sutdy in any moment you has time for choose the subject that you want start o study. Becuase is important know that you want study and that subject you will study. I disagree whit it is more importnat to choose to study subjects that me more want than to choose subject to prepare foir  a job or career.

First of all, when you enter to University, no answer that shubject you want or like study. The subject just was and you has begin when they said. In this moment you does not choose that like subject you want. Only you choose what career wants study. While if you will arrive at university and they said that you has choose subject, may be you choose some that no are important for you job or are not intereste by you career.

On the other hand, in my opinion is important kwon subject about of my work or my career, since if you choose that you like, you can get good results in your work and can be has problems with you managers. For example: you studied business adminitration and when you was in the university  you studied subject about of chemestry, this not will help made business becuase this subject is for teach different elements that there are in the chemestry.

In conclusion is importsnt study subject that are imporntant for your career or you job. In some cases no will like the subject but you has has fource for take """





