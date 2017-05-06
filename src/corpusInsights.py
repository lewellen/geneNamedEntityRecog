import collections
import itertools
import re
import operator

import common
import hiddenMarkovModel as hmm
import jointFreqMatrix
import unigramTraits as unigramTraitsModule

import numpy
import matplotlib.pyplot as plot
import scipy.stats


def plotProbColGivenRow(D, rowNames, colNames, xlabel, ylabel):
	# Create a bar chart where bars representing each row are presented 
	# side-by-side for each column in the nested dictionary D.

	sortedColNames = sorted(colNames)
	numCols = len(sortedColNames)
	indices = range(numCols)

	# P( col | row )
	E = jointFreqMatrix.toProbColGivenRow(D, rowNames, colNames)

	colWidth = 0.95
	barWidth = (colWidth / float(len(rowNames)))

	for rowNum, r in enumerate(rowNames):
		offsets = [ i + colWidth * (rowNum + 0 - 0.5 * len(rowNames)) / float(len(rowNames) - 1.0) for i in indices]
		sortedValues = [ E[r][c] for c in sortedColNames ]
		plot.bar(offsets, sortedValues, label = r, width = barWidth)

	plot.xticks(indices, sortedColNames)

	plot.xlabel(xlabel)
	plot.ylabel(ylabel)
	plot.legend(loc = "upper right") 
	plot.show()

def plotProbRowGivenCol(D, rowNames, colNames, xlabel, ylabel):
	# Create a stacked bar chart where bars represent each row are presentd stacked
	# for each column in the nested dictionary D. Will auto normalize so range is
	# [0,1].

	presentColumns = {}
	for r in rowNames:
		for c in colNames:
			if D[r][c] > 0:
				presentColumns.update({c : 0})

	sortedColNames = sorted(presentColumns.keys())
	numCols = len(sortedColNames)
	indices = range(numCols)

	# P( row | col )
	E = jointFreqMatrix.toProbRowGivenCol(D, rowNames, colNames)

	prev = numpy.zeros(numCols)
	for r in rowNames:
		sortedValues = [ E[r][c] for c in sortedColNames ]
		plot.bar(indices, sortedValues, label=r, bottom=prev, width=1)
		plot.xticks(indices, sortedColNames, rotation=70)
		prev = numpy.add(prev, sortedValues)

	plot.xlabel(xlabel)
	plot.ylabel(ylabel)
	plot.legend(loc = "upper right") 
	plot.show()

def plotCorrelMatrix(corr, tags):
	sortedTags = sorted(tags)
	numTags = len(sortedTags)
	indices = range(numTags)

	T = numpy.zeros((numTags, numTags))
	for i, a in enumerate(sortedTags):
		for j, p in enumerate(sortedTags):
			# these indices are swapped so it matches with the chart labels
			T[i, j] = corr[a][p]

	indices = range(numTags)
	indices = [ i + 0.5 for i in indices]

	f, subPlot = plot.subplots(1, 1)

	subPlot.set_xticks(indices)
	subPlot.set_xticklabels(sortedTags, rotation=90)
	subPlot.set_xlabel("Feature")
	subPlot.set_yticks(indices)
	subPlot.set_yticklabels(sortedTags)
	subPlot.set_ylabel("Feature")

	f.colorbar(
		subPlot.pcolormesh(T, cmap=plot.get_cmap('bwr'), vmin=-1, vmax=1), 
		ax=subPlot
		)
	f.tight_layout()

	plot.show()

def histTokenLenBySemanticLabel(train, tags):
	wordsByTag = { "Gene" : [], "NotGene" : [] }
	for taggedSentence in train:
		for taggedWord in taggedSentence.taggedWords:
			tag = "Gene"
			if taggedWord.tag == "O":
				tag = "NotGene"

			wordsByTag[tag].append(taggedWord.word)

	for tag in wordsByTag:
		xs = map(lambda x : len(x), wordsByTag[tag])
		plot.hist(xs, bins = 50, alpha = 0.5, label = tag)

	plot.ylabel("Frequency")
	plot.xlabel("Token length")
	plot.yscale("log")
	plot.xscale("log")
	plot.legend(loc = "upper right") 
	plot.show()

def histSymbolByTag(train, tags):
	symbols = map(lambda x : chr(x), xrange(33, 127))
	symbolsByTag = { tag : { symbol : 0 for symbol in symbols } for tag in tags }
	for taggedSentence in train:
		for taggedWord in taggedSentence.taggedWords:
			for letter in taggedWord.word:
				symbolsByTag[taggedWord.tag][letter] += 1

	plotProbRowGivenCol(
		symbolsByTag, 
		tags, symbols,
		"Symbol", "P(tag | symbol)"
	)

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

	plotProbRowGivenCol(
		unigramTraitsByTag, 
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

	plotCorrelMatrix(mat, presence.keys())

if __name__ == "__main__":
	labeledFilePath = "res/genetag.labeled"
	lFormat = common.LabeledFormat()
	train = list(lFormat.deserialize(labeledFilePath))
	tags = sorted(["I", "O", "B"])

	traitCorrelation(train, tags)

	# Insights on tokens
#	histTokenLenBySemanticLabel(train, tags)
#	histSymbolByTag(train, tags)
#	unigramTraitsByTag(train, tags)
#	mostFrequentByUnigramTraitAndTag(train, tags)

	# n-gram insights
#	mostCommonUnigrams(train, tags)
#	mostCommonBigrams(train, tags)
#	mostCommonTrigrams(train, tags)
