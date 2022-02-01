# Python Linguistic Analysis Tools (pylats)
Pylats is designed to perform text pre-processing for further linguistic analyses (e.g., measuring lexical diversity and/or lexical sophistication).  Currently, advanced features such as lemmatization and POS tagging are available for English, with other languages to follow (Spanish models will be added in the near future, we have plans to release other models as well). However, pylats CAN currently be used with other languages using basic features (see examples below).

Pylats currently uses [spacy](https://spacy.io/) as a starting point for many of its advanced features if working with English. Pylats was tested using spacy version 3.2 and be default uses the "en_core_web_sm" model. To install spacy and a language model, see the [spacy installation instructions](https://spacy.io/).

## Installation
To install pylats, you can use `pip`:

```bash
pip install pylats
```

## Getting Started
### Import
```python
from pylats import lats
```
### Using pylats
`pylats` is designed to be the first step in conducting linguistic analyses using related analysis tools (such as `lexical-diversity`).

`pylats` uses the `Normalize` class to take a raw text string and format it:

```python
teststr = "I love pepperoni pizza."
normed = lats.Normalize(teststr) #processed text string
print(normed.toks)
```

```
#output:
['i', 'love', 'pepperoni', 'pizza']
```

### Paragraphs and sentences
The `.toks` method will provide a flat list of the tokens in a text. However, it can often be useful to conduct analyses at the sentence and/or paragraph level. The `.sents` and `.paras` methods provide a representation of text with nested lists.

```python
teststr = """I love pepperoni pizza. Sometimes I like to add feta and banana peppers.
This is a second paragraph. In the original string there is a newline character before this paragraph."""

normedp = lats.Normalize(para_sample)
```
#### tokens

```python
print(normedp.toks)
```
```
['i', 'love', 'pepperoni', 'pizza', 'sometimes', 'i', 'like', 'to', 'add', 'feta', 'and', 'banana', 'peppers', 'this', 'is', 'a', 'second', 'paragraph', 'in', 'the', 'original', 'string', 'there', 'is', 'a', 'newline', 'character', 'before', 'this', 'paragraph']
```
#### sentences
```python
for x in normedp.sents:
	print(x) #print tokens in each sentence
```

```
['i', 'love', 'pepperoni', 'pizza']
['sometimes', 'i', 'like', 'to', 'add', 'feta', 'and', 'banana', 'peppers']
['this', 'is', 'a', 'second', 'paragraph']
['in', 'the', 'original', 'string', 'there', 'is', 'a', 'newline', 'character', 'before', 'this', 'paragraph']
```

#### paragraphs
```
for x in normed.paras:
	print(x) #print sentences each paragraph
```
```
[['i', 'love', 'pepperoni', 'pizza'], ['sometimes', 'i', 'like', 'to', 'add', 'feta', 'and', 'banana', 'peppers']]
[['this', 'is', 'a', 'second', 'paragraph'], ['in', 'the', 'original', 'string', 'there', 'is', 'a', 'newline', 'character', 'before', 'this', 'paragraph']]
```

### Changing parameters
By default, `Normalize` simply removes punctuation and converts words in the text to lower case. However, a wide range of customizations can be made by adjusting the `parameters` class.

For example, it may be useful to exclude particular words for some analyses. In studies of lexical diversity, for instance, we probably don't want to include misspelled words (misspelled words would positively contribute to diversity scores, but probably shouldn't). Pylats includes a default list of "real" words drawn from a large corpus of English language which can be used to filter out misspelled ones. Words can also be added to a list of items to remove OR can be added to a list that overrides other lists.

Below, we create a copy of `parameters` and then make some changes:

```python
new_params = lats.parameters() #create a copy of the parameters class
new_params.attested = True #set the attested attribute to True
```
**Output with default settings:**

```python
#with default settings
msp_default = lats.Normalize("This is a smaple sentence")
print(msp_default.toks)
```

```
['this', 'is', 'a', 'smaple', 'sentence']
```

**Output with new settings:**

```python
msp_new = lats.Normalize("This is a smaple sentence", params = new_params)
print(msp_new.toks)
```

```
['this', 'is', 'a', 'sentence']
```

#### Default parameters
```python
class parameters:
	punctuation = ['``', "''", "'", '.', ',', '?', '!', ')', '(', '%', '/', '-', '_', '-LRB-', '-RRB-', 'SYM', ':', ';', '"']
	punctse = [".","?","!"]
	abbrvs = ["mrs.","ms.","mr.","dr.","phd."]
	splitter = "\n" #for splitting paragraphs
	rwl = realwords
	sp = True
	sspl = "spacy"
	pos = None #other options are "pos" for Penn tags and "upos" for universal tags
	removel = ['becuase'] #typos and other words not caught by the real words list
	lemma = False
	lower = True #treat all words as lower case
	attested = False #filter output using real words list?
	spaces = [" "] #need to add more here
	override = [] #items the system ignores that should be overridden
``` 

### Adding part of speech information
If spacy is installed (and activated), part of speech tags can be added to each token, which can be useful in disambiguating homographic tokens (e.g., **_run_** as a verb in the sentence _I like to **run**._ versus run as a noun in the sentence _I went for a **run**._ ). This is helpful in a number of applications, including calculating indices lexical diversity.

```python
pos_params = lats.parameters() #still need to fix this
pos_params.pos = "upos" #for large-grained universal parts of speech
run_sample = lats.Normalize("I like to run. I went for a run.", params = pos_params)
for x in run_sample.sents:
	print(x)
```

```
['i_PRON', 'like_VERB', 'to_PART', 'run_VERB']
['i_PRON', 'went_VERB', 'for_ADP', 'a_DET', 'run_NOUN']
```
### Changing the spacy language model

To change the spacy language model that is used by pylats, first make sure that the desired model has been downloaded from [spacy](https://spacy.io/). Then, load the model:

```python
#loading the "en_core_web_trf" model
lats.nlp = lats.spacy.load("en_core_web_trf")
```
## Using pylats with languages other than English
The early versions of pylats have an advanced features for English texts and basic features for other languages. As the tool expands, advanced feature support will be added for other languages (for example, advanced features will be added for Spanish in the near future).

To process texts with basic features, simply change parameters.sp to `True`. The processor will treat text between whitespace as a token. Accordingly, some pre-processing may be necessary.

**Example 1 (Spanish)**:
```python
whtsp_params = lats.parameters() #copy parameters
whtsp_params.sp = False #turn off spacy processing
span_sample = lats.Normalize("Me gustaría aqua con gas",whtsp_params)
print(span_sample.toks)
```

```
['me', 'gustaría', 'aqua', 'con', 'gas']
```

**Example 2 (Korean)**:

```python
whtsp_params = lats.parameters() #copy parameters
whtsp_params.sp = False #turn off spacy processing
kor_sample = lats.Normalize("피자 좀 주세요",whtsp_params)
print(kor_sample.toks)
```

```
['피자', '좀', '주세요']
```






