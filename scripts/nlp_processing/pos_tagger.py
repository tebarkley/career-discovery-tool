#!/usr/bin/env python 
'''Script to run from command line to add two columns of pos tagged words to a dataframe containing job descriptions'''

import nltk
import pandas as pd
from pandas import DataFrame, Series
from os import path, pardir
import pickle
from nltk.corpus import wordnet as wn
import sys


def regular_pos_tagger(input_file_path, tagger_file_path):
	'''Function to part of speech tag words stored in a pickled dataframe'''
	data = pd.read_pickle(input_file_path)
	f = open(tagger_file_path, 'r')
	ngram_tagger = pickle.load(f)
	f.close()
	data['ngram_tags'] = data.words.map(lambda x: [ngram_tagger.tag(word) for word in x])
	return data

def verb_pos_improver(sents):
	'''Function that takes a pos tagged job description and improves the tagging for sentences that start with verbs. 
	This is important for extracting work activities from job descriptions'''
	fixed_tags = []
	for sent in sents:
		try:
			first_word = sent[0][0]
			first_tag = sent[0][1]
		except:
			return ''
		if first_tag.startswith('N') and len(sent)>1:
			next_tag = sent[1][1]
			new_sent = []
			if len(wn.synsets(first_word.lower(), pos=wn.VERB)) > len(wn.synsets(first_word.lower(), pos=wn.NOUN)):
				first_tag = 'VB'
			new_sent.append((first_word, first_tag))
			[new_sent.append((word,tag)) for word, tag in sent[1:]] 
			fixed_tags.append(new_sent)
		else:
			fixed_tags.append(sent)
	return fixed_tags


def main(argv):
	input_file_path = argv[0]
	tagger_file_path = argv[1]
	output_file_path = argv[2]
	pos_tagged_frame = regular_pos_tagger(input_file_path, tagger_file_path)
	pos_tagged_frame['ngram_tags_verbs'] = pos_tagged_frame.ngram_tags.map(verb_pos_improver)
	pos_tagged_frame.to_pickle(output_file_path)

if __name__ == "__main__":
	main(sys.argv[1:])