#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 10:35:53 2021

@author: kkyle2

prototype for text processing in SALAT tools
first, we build a simple processor, then we build one for spacy

"""
import math
import pickle
import operator
import statistics as stat
import itertools #for zip() function
from collections import Counter
import pkg_resources #for importing data from packages

#Try to import spacy and load a model
model = "en_core_web_sm"

try: 
	import spacy
	spld = True
except ModuleNotFoundError:
	print("Spacy has not been installed.\nTo access advanced features, please install Spacy.")
	spld = False

if spld == True:
	try:
		nlp = spacy.load(model)
		mdld = True
	except OSError:
		print("The chosen model does not seem to be available on your system.\nPlease see Spacy documentation for assistance.")
		mdld = False

#Try to import plotnine
try:
	from plotnine import ggplot, aes, stat_bin, geom_bar,geom_histogram,geom_vline,geom_density,xlab
	pltn = True
except ModuleNotFoundError:
	print("plotnine has not been installed.\nTo enable advanced data visualization features, please install plotnine.")
	pltn = False

#load datafiles
def get_fname(packagename,filename): #look in package, then in local working directory
	try: 
		data_filename = pkg_resources.resource_filename(packagename, filename)
	except ModuleNotFoundError:
		print("NOTE:",filename,"not found in package, using local file")
		data_filename = filename
	return(data_filename)

realwordsn = get_fname('TAALED',"real_words5.pickle") #words in written COCA that occur at least 5 times
realwords = pickle.load(open(realwordsn,"rb")) #words that occur in written COCA at least twice

class parameters:
	punctuation = ['``', "''", "'", '.', ',', '?', '!', ')', '(', '%', '/', '-', '_', '-LRB-', '-RRB-', 'SYM', ':', ';', '"']
	punctse = [".","?","!"]
	abbrvs = ["mrs.","ms.","mr.","dr.","phd."]
	splitter = "\n" #for splitting paragraphs
	rwl = realwords
	sp = True
	sspl = "spacy"
	removel = ['becuase'] #typos and other words not caught by the real words list
	lemma = False
	attested = True #filter output using real words list?
	spaces = [" "] #need to add more here
	override = [] #items the system ignores that should be overridden

class TokObject(): #need to add
	def __init__(self, token = None,counter = 0, params = parameters): #see parameters object for all relevant variables
		self.idx = counter #position in sentence
		
		if "spacy" in str(type(token)): #check for spacy token
			self.text = token.text #raw text
			self.lemma_ = token.lemma_ #raw text #lemma form (same as spacy)
			self.pos_ = token.pos_ #Universal pos tag (same as spacy)
			self.tag_ = token.tag_ #Specific POS tag (same as spacy)
			self.dep_ = token.dep_ #dependency relationship (same as spacy)
			self.head = token.head #head object (same as spacy)
			self.nchars = len(token.text) #length of item in chars
			#still need to deal with:
			self.type = None #function word, content word, or punctuation?

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
		#punctuation
		if self.text in params.punctuation:
			self.ispunct = True
		else:
			self.ispunct = False
		#spaces
		if self.text in params.spaces:
			self.isspace = True
		else:
			self.isspace = False
			
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
			for token in nlp(text):
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
	
	### Start HERE!!! ###
	#pipeline for sentences and tokens
	def text2toks(self, text, params = parameters): #sspl options include: spacy, simple - will add more in the future
		#punctse = params.punctse,punctuation = params.punctuation, realwords = params.rwl, sp = params.sp, sspl = params.sspl
		tok_texts = []
		if params.sp == True: #message if spacy is selected but not available
			if spld == False or mdld == False: #global variables that indicate whether spacy itself and a spacy model has been loaded
				print("Spacy processing selected, but either spacy and/or the spacy nlp model is not available. Defaulting to simple rule-based tokenization.")
				params.sp = False
				params.sspl = "simple" #this is not ideal in this case
		
		if params.sp == True:
			if params.sspl == "spacy":
				doc = nlp(text)
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
	
	def normalize(self,fl_paras, params = parameters): #presumes a list with three levels [para[sent[token]]]
		normalized = []
		ignored = []
		for paras in fl_paras:
			sents = []
			for sent in paras:
				toks = []
				for tok in sent:
					#if item in override, then don't worry about other checks:
					if tok.text in params.override:
						if params.lemma == True:
							toks.append(tok.lemma_.lower())
						else:
							toks.append(tok.text.lower())
						continue
					#otherwise:
					if tok.text in params.removel:
						ignored.append((tok.text,"(in remove list)"))
						continue
					if tok.ispunct == True or tok.isspace == True:
						#ignored.append((tok.text,"(in punctuation list)"))
						continue
					if params.attested == True and tok.isreal == False:
						ignored.append((tok.text,"(not in real word list)"))
						continue
					if params.lemma == True:
						toks.append(tok.lemma_.lower())
					else:
						toks.append(tok.text.lower())
				sents.append(toks)
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

#feature rich lexdiv functions
class lexdiv():
	
	def safe_divide(self, numerator, denominator):
		if denominator == 0 or denominator == 0.0:
			index = 0
		else: index = numerator/denominator
		return index
	
	def frequency(self,text):
		freq_d = {}
		for tok in text:
			if tok not in freq_d:
				freq_d[tok] = 1
			else:
				freq_d[tok] += 1
		return(freq_d)
	
	def sorter(self,freq_d):
		sorts =  sorted(freq_d.items(), key=operator.itemgetter(1))
		return(sorts)

	def TTR(self, text):
		ntokens = len(text)
		ntypes = len(set(text))
		
		return(self.safe_divide(ntypes,ntokens))

	def RTTR(self, text):
		ntokens = len(text)
		ntypes = len(set(text))
		
		return(self.safe_divide(ntypes, math.sqrt(ntokens)))

	def MAAS(self, text):
		ntokens = len(text)
		ntypes = len(set(text))
		return(self.safe_divide((math.log10(ntokens)-math.log10(ntypes)), math.pow(math.log10(ntokens),2)))

	def LTTR(self, text):
		ntokens = len(text)
		ntypes = len(set(text))
		
		return(self.safe_divide(math.log10(ntypes), math.log10(ntokens)))

	def MATTR(self, text, window_length = 50, outputs = True):
		vals = []
		windows = []
		if len(text) < (window_length + 1):
			index = self.safe_divide(len(set(text)),len(text))
			return(index,[index],[text])
	
		else:
			for x in range(len(text)):
				small_text = text[x:(x + window_length)]
				if len(small_text) < window_length:
					break
				windows.append(small_text)
				vals.append(self.safe_divide(len(set(small_text)),float(window_length))) 
				index = stat.mean(vals)
			if outputs == True:
				return(index,vals,windows)
			else:
				return(index)

	def MSTTR(self, text, window_length = 50): #add functionality here (lists, etc.)
	
		if len(text) < (window_length + 1):
			ms_ttr = self.safe_divide(len(set(text)),len(text))
	
		else:
			sum_ttr = 0
			denom = 0
	
			n_segments = int(self.safe_divide(len(text),window_length))
			seed = 0
			for x in range(n_segments):
				sub_text = text[seed:seed+window_length]
				#print sub_text
				sum_ttr += self.safe_divide(len(set(sub_text)), len(sub_text))
				denom+=1
				seed+=window_length
	
			ms_ttr = self.safe_divide(sum_ttr, denom)
	
		return(ms_ttr)
	
	def HDD(self,text, samples = 42): #add info to output (probability for each word?)
		#requires Counter import
		def choose(n, k): #calculate binomial
			"""
			A fast way to calculate binomial coefficients by Andrew Dalke (contrib).
			"""
			if 0 <= k <= n:
				ntok = 1
				ktok = 1
				for t in range(1, min(k, n - k) + 1): #this was changed to "range" from "xrange" for py3
					ntok *= n
					ktok *= t
					n -= 1
				return ntok // ktok
			else:
				return 0
	
		def hyper(successes, sample_size, population_size, freq): #calculate hypergeometric distribution
			#probability a word will occur at least once in a sample of a particular size
			try:
				prob_1 = 1.0 - (float((choose(freq, successes) * choose((population_size - freq),(sample_size - successes)))) / float(choose(population_size, sample_size)))
				prob_1 = prob_1 * (1/sample_size)
			except ZeroDivisionError:
				prob_1 = 0
				
			return prob_1
	
		prob_sum = 0.0
		ntokens = len(text)
		types_list = list(set(text))
		frequency_dict = Counter(text)
	
		for items in types_list:
			prob = hyper(0,samples,ntokens,frequency_dict[items]) #random sample is 42 items in length
			prob_sum += prob
	
		return(prob_sum)
	
	def MTLDER(self, text, mn=10,ttrval = .720):
		ft = [] #factor texts
		fl = [] #factor lengths
		fp = [] #factor proportions
		start = 0
		for x in range(len(text)):
			factor_text = text[start:x+1]
			if x+1 == len(text):
				ft.append(factor_text) #add factor text to list
				fact_prop = self.safe_divide((1 - self.TTR(factor_text)),(1 - ttrval)) #proportion of factor
				fp.append(fact_prop)
				fl.append(len(factor_text)) #add partial factor length to list
			else:
				if self.TTR(factor_text) < ttrval and len(factor_text) >= mn:
					ft.append(factor_text) #add factor text to list
					fl.append(len(factor_text))
					fp.append(1)
					start = x+1
				else:
					continue

		return(ft,fl,fp)
	
	#original approach taken by McCarthy and Jarvis (number of words in text divided by number of factors):
	def MTLD_O(self,windowl,factorprop): #window length, factor proportion
		nwords = sum(windowl)
		nfactors = sum(factorprop)
		return(nwords/nfactors)
	
	#mean factor length approach:
	def MTLD_MFL(self,windowl,factorprop, listout = False): #window length, factor proportion
		factorls = [] #holder for factor lengths
		for wl, fp in zip(windowl,factorprop): #iterate through window lengths and factor proportions
			#print(wl/fp)	
			factorls.append(wl/fp) #window length/factor proportion
		if listout == True:
			return(factorls)
		else:
			return(sum(factorls)/len(factorls))

	
	def MTLD(self, text, mn = 10,ttrval = .720, outputs = False): 
		
		fwft,fwfl,fwfp = self.MTLDER(text,mn,ttrval) #factor text list, factor length list, factor proportion list
		bwft,bwfl,bwfp = self.MTLDER(list(reversed(text)),mn,ttrval) #backward text
		
		valo = stat.mean([self.MTLD_O(fwfl,fwfp),self.MTLD_O(bwfl,bwfp)])
		valmfl = stat.mean([self.MTLD_MFL(fwfl,fwfp),self.MTLD_MFL(bwfl,bwfp)]) #average of forward and backward
		valmfl2 = self.MTLD_MFL(fwfl+bwfl,fwfp+bwfp) #mean for all factors (including forward and backward)
		
		if outputs == True:
			return(valmfl2,valmfl,valo,self.MTLD_MFL(fwfl+bwfl,fwfp+bwfp,listout=True),[fwft,fwfl,fwfp,bwft,bwfl,bwfp])
		return(valmfl2)
	
	def __init__(self, text = None, window_length = 50,mn = 10,ttrval = .720,samples = 42):
		if text != None:
			if type(text) != list:
				self.text = text.split(" ")
			else:
				self.text = text
			#basic stats
			self.ntokens = len(self.text) #token count
			self.ntypes = len(list(set(self.text)))
			self.ttr = self.TTR(self.text)
			self.rttr = self.RTTR(self.text)
			self.lttr = self.LTTR(self.text)
			self.maas = self.MAAS(self.text)
			self.msttr = self.MSTTR(self.text,window_length)
			self.hdd = self.HDD(self.text,samples)
			#frequency
			self.freqd = self.frequency(self.text)
			self.freqs = sorted(self.freqd.items(), key=operator.itemgetter(1),reverse = True)
			#mattr stuff
			self.mattr,self.mattrs,self.mattrwins = self.MATTR(self.text,window_length,outputs = True)
			self.nmattrwins = len(self.mattrs) #number of windows for mattr
			self.mattrplot = ggplot() + aes(x=self.mattrs) + geom_density(fill = "#56B4E9",alpha = .2) + geom_vline(xintercept = self.mattr,color = "red",linetype="dashed") + xlab("Density Plot")
			#mtld stuff
			self.mtld,self.mtldav,self.mtldo,self.mtldvals,self.mtldlists = self.MTLD(self.text,mn,ttrval,outputs = True)
			self.mtldplot = ggplot() + aes(x=self.mtldvals) + geom_density(fill = "#56B4E9",alpha = .2) + geom_vline(xintercept = self.mtld,color = "red",linetype="dashed") + xlab("Density Plot")

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

#Work on realword list:
# freqd = pickle.load(open("written_freq_complete.pickle","rb"))
# def refiner(fd, fl):
# 	rwd = {} #dict of real words.
# 	
# 	for x in fd:
# 		if fd[x] >= fl:
# 			rwd[x.split("_")[0].lower()] = None
# 	return(rwd)

# rwl = refiner(freqd,5)
# pickle.dump(rwl, open("real_words5.pickle","wb"))
#samples:
textsmpl = """When you will go sutdy in any moment you has time for choose the subject that you want start o study. Becuase is important know that you want study and that subject you will study. I disagree whit it is more importnat to choose to study subjects that me more want than to choose subject to prepare foir  a job or career.

First of all, when you enter to University, no answer that shubject you want or like study. The subject just was and you has begin when they said. In this moment you does not choose that like subject you want. Only you choose what career wants study. While if you will arrive at university and they said that you has choose subject, may be you choose some that no are important for you job or are not intereste by you career.

On the other hand, in my opinion is important kwon subject about of my work or my career, since if you choose that you like, you can get good results in your work and can be has problems with you managers. For example: you studied business adminitration and when you was in the university  you studied subject about of chemestry, this not will help made business becuase this subject is for teach different elements that there are in the chemestry.

In conclusion is importsnt study subject that are imporntant for your career or you job. In some cases no will like the subject but you has has fource for take """

#simple

# normsmpl = Normalize(textsmpl)
# normsmpl.toks
# normsmpl.paras
# normsmpl.sents
# normsmpl.ignored
# normsmpl.toksto[:10]

# for x in normsmpl.toksto[:10]:
# 	print(x.text, x.isreal)

# ldvals = lexdiv(normsmpl.toks)
# ldvals.mtld
# ldvals.mtldo #in Mcarthy & Jarvis (2010) + TAALED <= 1.4; 
# ldvals.mattr
# ldvals.mattrplot
# ldvals.mtldplot
# ldvals.mtldvals
######
#samples and tests:
# #test Normalize class
# processed = Normalize(textsmpl)
# processed.paratxt
# processed.senttxt
# processed.toks
# processed.toktxt
# processed.paras
# processed.sents
# processed.toks


#ld tests here
# ldvals = lexdiv(normsmpl)
# ldvals.hdd
# ldvals.mtld
# ldvals.mtldo
# ldvals.mtldav #this will be the same as mtld when there are the same number of factors forwards and backwards
# ldvals.mtldvals
# ldvals.mattr
# ldvals.mattrs
# ldvals.mattrwins
# ldvals.nmattrwins
# ldvals.ntokens
# ldvals.ntypes
# ldvals.freqs
# ldvals.ttr
# ldvals.rttr
# ldvals.lttr
# ldvals.maas
# ldvals.msttr
# ldvals.mattrplot
# ldvals.mtldplot
# ldvals.freqs



