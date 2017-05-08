import collections
import itertools
import re
import operator

import common
import hiddenMarkovModel as hmm
import plotUtils
import unigramTraits as unigramTraitsModule
import jointFreqMatrix

import scipy.stats

def histSymbolByTag(train, tags):
	symbols = map(lambda x : chr(x), xrange(33, 127))
	symbolsByTag = { tag : { symbol : 0 for symbol in symbols } for tag in tags }
	for taggedSentence in train:
		for taggedWord in taggedSentence.taggedWords:
			for letter in taggedWord.word:
				symbolsByTag[taggedWord.tag][letter] += 1

	probOfTagGivenSymbol = jointFreqMatrix.toProbRowGivenCol(
		symbolsByTag, tags, symbols) 

	plotUtils.plotStackedBarChart(
		probOfTagGivenSymbol, 
		tags, symbols,
		"Symbol", "P(tag | symbol)"
	)

def mostCommonUnigrams(train, tags):
	unigrams = { v : collections.Counter() for v in tags }
	for taggedSentence in train:
		W = taggedSentence.taggedWords
		for u in W:
			unigram = u.word
			unigrams[u.tag].update([unigram])

	for u in tags:
		mostCommon = unigrams[u].most_common(10)
		mostCommon = map(lambda (unigram, freq) : "\"%s\"" % unigram, mostCommon)
		summary = ", ".join(mostCommon)
		print("%s: %s" % (u, summary))

def mostCommonBigrams(train, tags):
	bigrams = { u : { v : collections.Counter() for v in tags } for u in tags }
	for taggedSentence in train:
		W = taggedSentence.taggedWords
		for (u, v) in zip(W, W[1:]):
			bigram = "%s %s" % (u.word, v.word)
			bigrams[u.tag][v.tag].update([bigram])

	for u in tags:
		for v in tags:
			mostCommon = bigrams[u][v].most_common(10)
			mostCommon = map(lambda (bigram, freq) : "\"%s\"" % bigram, mostCommon)
			summary = ", ".join(mostCommon)
			print("%s %s: %s" % (u, v, summary))


def mostCommonTrigrams(train, tags):
	trigrams = { u : { v : { w : collections.Counter() for w in tags } for v in tags } for u in tags }
	for taggedSentence in train:
		W = taggedSentence.taggedWords
		for (u, v, w) in zip(W, W[1:], W[2:]):
			trigram = "%s %s %s" % (u.word, v.word, w.word)
			trigrams[u.tag][v.tag][w.tag].update([trigram])

	for u in tags:
		for v in tags:
			for w in tags:
				mostCommon = trigrams[u][v][w].most_common(8)
				mostCommon = map(lambda (trigram, freq) : "\"%s\"" % trigram, mostCommon)
				summary = ", ".join(mostCommon)
				print("%s %s %s: %s" % (u, v, w, summary))

def unigramTraitsByTag(train, tags):
	unigramTraits = unigramTraitsModule.unigramTraitList
	traitNames = [ unigramTrait.getName() for unigramTrait in unigramTraits ]
	for unigramTrait in unigramTraits:
		unigramTrait.selfSelect(train, tags)

	unigramTraitsByTag = { t : { f : 0 for f in traitNames } for t in tags }
	for taggedSentence in train:
		for taggedWord in taggedSentence.taggedWords:
			word = taggedWord.word
			tag = taggedWord.tag
			for unigramTrait in unigramTraits:
				wasMatch, matchedWith = unigramTrait.isAMatch(word)
				if wasMatch:
					unigramTraitsByTag[tag][unigramTrait.getName()] += 1

	probOfTagGivenTrait = jointFreqMatrix.toProbRowGivenCol(
		unigramTraitsByTag, tags, traitNames) 

	plotUtils.plotStackedBarChart(
		probOfTagGivenTrait, 
		tags, traitNames, 
		"Unigram Traits", "P(tag | unigramTrait)"
	)

def mostFrequentByUnigramTraitAndTag(train, tags):
	unigramTraits = unigramTraitsModule.unigramTraitList
	traitNames = [ unigramTrait.getName() for unigramTrait in unigramTraits ]
	for unigramTrait in unigramTraits:
		unigramTrait.selfSelect(train, tags)

	unigramTraitsByTag = { t : { f : collections.Counter() for f in traitNames } for t in tags }
	for taggedSentence in train:
		for taggedWord in taggedSentence.taggedWords:
			word = taggedWord.word
			tag = taggedWord.tag
			for unigramTrait in unigramTraits:
				wasMatch, matchedWith = unigramTrait.isAMatch(word)
				if wasMatch:
					unigramTraitsByTag[tag][unigramTrait.getName()].update([word])

	for tag in tags:
		print("%s" % tag)
		for unigramTrait in unigramTraits:
			mostCommon = unigramTraitsByTag[tag][unigramTrait.getName()].most_common(10)
			print("%s\t:" % unigramTrait.getName()),
			print(", ".join(map(lambda (word, count): "(%d) \"%s\"" % (count, word), mostCommon)))

def traitCorrelation(train, tags):
	unigramTraits = unigramTraitsModule.unigramTraitList

	presence = { trait.getName() : [] for trait in unigramTraits }
	presence.update({ "tag_" + tag : [] for tag in tags })

	for taggedSentence in train:
		for taggedWord in taggedSentence.taggedWords:
			for trait in unigramTraits:
				isMatch, match = trait.isAMatch(taggedWord.word)
				value = 0
				if isMatch:
					value = 1
				presence[trait.getName()].append(value)

			for tag in tags:
				value = 0
				if tag == taggedWord.tag:
					value = 1
				presence["tag_" + tag].append(value)

	mat = { a : { b : 0 for b in presence } for a in presence }
	for a in presence:
		for b in presence:
			#coeff, pvalue = scipy.stats.pearsonr(presence[a], presence[b])
			coeff, pvalue = scipy.stats.spearmanr(presence[a], presence[b])
			mat[a][b] = coeff

	plotUtils.plotCorrelMatrix(mat, presence.keys())

if __name__ == "__main__":
	labeledFilePath = "res/genetag.labeled"
	lFormat = common.LabeledFormat()
	train = list(lFormat.deserialize(labeledFilePath))
	tags = sorted(["I", "O", "B"])

	# Insights on tokens
	histSymbolByTag(train, tags)

	# n-gram insights
	mostCommonUnigrams(train, tags)
	mostCommonBigrams(train, tags)
	mostCommonTrigrams(train, tags)

	# Insights on features/traits
	unigramTraitsByTag(train, tags)
	mostFrequentByUnigramTraitAndTag(train, tags)
	traitCorrelation(train, tags)
