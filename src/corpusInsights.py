import collections
import itertools
import re
import operator

import common
import hiddenMarkovModel as hmm
import jointFreqMatrix
from features import AllUpperLettersFeature, AllLowerLettersFeature, CapitalizedFeature, PositiveIntegerFeature, PuncFeature, RomanNumFeature, AlphaNumericFeature, EnglishSuffixFeature, LatinPrefixFeature, LatinSuffixFeature, GreekLetterFeature, DeterminerFeature, PrepositionFeature, ConjunctionFeature, ChemicalFormulaFeature

import numpy
import matplotlib.pyplot as plot


def histTokenLenBySemanticLabel(labeledFilePath):
	wordsByTag = { "Gene" : [], "NotGene" : [] }
	lFormat = common.LabeledFormat()
	for taggedSentence in lFormat.deserialize(labeledFilePath):
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

def histSymbolByTag(labeledFilePath):
	tags = [ "I", "O", "B" ]

	symbolsByTag = { tag : { chr(i) : 0 for i in xrange(33, 127) } for tag in tags }

	labeledFilePath = "res/genetag.labeled"
	lFormat = common.LabeledFormat()
	for taggedSentence in lFormat.deserialize(labeledFilePath):
		for taggedWord in taggedSentence.taggedWords:
			for letter in taggedWord.word:
				symbolsByTag[taggedWord.tag][letter] += 1

	for i in xrange(33, 127):
		s = 0.0
		for tag in symbolsByTag:
			s += symbolsByTag[tag][chr(i)]

		if s > 0:
			for tag in symbolsByTag:
				symbolsByTag[tag][chr(i)] /= s

	prev = numpy.array( [ 0 for x in xrange(33, 127) ] )
	for tag in symbolsByTag:
		S = symbolsByTag[tag]
		sortedKeys = sorted(S.keys())
		sortedValuesByKeys = [ S[k] for k in sortedKeys ]
		
		columns = range(len(sortedKeys))
		plot.bar(columns, sortedValuesByKeys, label=tag, bottom=prev, width=1)
		plot.xticks(columns, sortedKeys)

		prev = numpy.add(prev, sortedValuesByKeys)

	plot.ylabel("P(char | tag)")
	plot.xlabel("Symbol")
	plot.legend(loc = "upper right") 
	plot.show()

def plotProbColGivenRow(D, rowNames, colNames, xlabel, ylabel):
	sortedColNames = sorted(colNames)
	numCols = len(sortedColNames)
	indices = range(numCols)

	# P( col | row )
	E = jointToProbColGivenRow(D, rowNames, colNames)

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
		plot.xticks(indices, sortedColNames)
		prev = numpy.add(prev, sortedValues)

	plot.xlabel(xlabel)
	plot.ylabel(ylabel)
	plot.legend(loc = "upper right") 
	plot.show()

def featuresByTag(labeledFilePath):
	lFormat = common.LabeledFormat()
	taggedSentences = [ taggedSentence for taggedSentence in lFormat.deserialize(labeledFilePath) ]

	features = [
		AllUpperLettersFeature(), AllLowerLettersFeature(), CapitalizedFeature(), PositiveIntegerFeature(),
		PuncFeature(), RomanNumFeature(), AlphaNumericFeature(), EnglishSuffixFeature(),
		LatinPrefixFeature(), LatinSuffixFeature(), GreekLetterFeature(),
		DeterminerFeature(), PrepositionFeature(), ConjunctionFeature(),
		ChemicalFormulaFeature()
		]

	featureNames = [ feature.getName() for feature in features ]
	tags = sorted(["I", "O", "B"])
	featuresByTag = { t : { f : 0 for f in featureNames } for t in tags }

	for feature in features:
		feature.selfSelect(taggedSentences, tags)

	for taggedSentence in taggedSentences:
		for taggedWord in taggedSentence.taggedWords:
			word = taggedWord.word
			tag = taggedWord.tag
			for feature in features:
				wasMatch, matchedWith = feature.hasFeature(word)
				if wasMatch:
					featuresByTag[tag][feature.getName()] += 1

	plotProbRowGivenCol(
		featuresByTag, 
		tags, featureNames, 
		"Features", "P(tag | feature)"
	)

def mostFrequentByFeatureAndTag(labeledFilePath):
	lFormat = common.LabeledFormat()
	taggedSentences = [ taggedSentence for taggedSentence in lFormat.deserialize(labeledFilePath) ]

	features = [
		AllUpperLettersFeature(), AllLowerLettersFeature(), CapitalizedFeature(), PositiveIntegerFeature(),
		PuncFeature(), RomanNumFeature(), AlphaNumericFeature(), EnglishSuffixFeature(),
		LatinPrefixFeature(), LatinSuffixFeature(), GreekLetterFeature(),
		DeterminerFeature(), PrepositionFeature(), ConjunctionFeature(),
		ChemicalFormulaFeature()
		]

	featureNames = [ feature.getName() for feature in features ]
	tags = sorted(["I", "O", "B"])
	featuresByTag = { t : { f : collections.Counter() for f in featureNames } for t in tags }

	for feature in features:
		feature.selfSelect(taggedSentences, tags)

	for taggedSentence in taggedSentences:
		for taggedWord in taggedSentence.taggedWords:
			word = taggedWord.word
			tag = taggedWord.tag
			for feature in features:
				wasMatch, matchedWith = feature.hasFeature(word)
				if wasMatch:
					featuresByTag[tag][feature.getName()].update([word.lower()])

	for tag in tags:
		print("%s" % tag)
		for feature in features:
			mostCommon = featuresByTag[tag][feature.getName()].most_common(10)
			print("%s\t:" % feature.getName()),
			print(", ".join(map(lambda (word, count): "(%d) \"%s\"" % (count, word), mostCommon)))
		



def mostCommonUnigrams(labeledFilePath):
	lFormat = common.LabeledFormat()
	corpusStats = hmm.CorpusStatistics(
		[ taggedSentence for taggedSentence in lFormat.deserialize(labeledFilePath) ],
		True	
		)

	numProbs = 10
	numExamplesPerProb = 5
	
	for tag in corpusStats.wordGivenTag:
		print("%s" % tag)

		wordsByProb = {}
		for word in corpusStats.wordGivenTag[tag]:
			prob = round(corpusStats.wordGivenTag[tag][word], 3)
			if not prob in wordsByProb:
				wordsByProb.update({ prob : [] })

			wordsByProb[prob].append(word)

		descProbs = sorted(wordsByProb.keys(), reverse=True)
		topProbs = descProbs[:numProbs]
		for prob in topProbs:
			print("\t%.3f\t(%d): %s" % (
				prob, 
				len(wordsByProb[prob]), 
				", ".join(wordsByProb[prob][:numExamplesPerProb])
			))

def mostCommonBigrams(labeledFilePath):
	tags = sorted(["I", "O", "B"])
	indices = range(len(tags))

	bigrams = { u : { v : collections.Counter() for v in tags } for u in tags }

	lFormat = common.LabeledFormat()
	for taggedSentence in lFormat.deserialize(labeledFilePath):
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


def mostCommonTrigrams(labeledFilePath):
	tags = sorted(["I", "O", "B"])
	indices = range(len(tags))

	trigrams = { u : { v : { w : collections.Counter() for w in tags } for v in tags } for u in tags }

	lFormat = common.LabeledFormat()
	for taggedSentence in lFormat.deserialize(labeledFilePath):
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

if __name__ == "__main__":
	labeledFilePath = "res/genetag.labeled"

	# Insights on tokens
	#histTokenLenBySemanticLabel(labeledFilePath)
	#histSymbolByTag(labeledFilePath)
	featuresByTag(labeledFilePath)
	mostFrequentByFeatureAndTag(labeledFilePath)

	# n-gram insights
	#mostCommonUnigrams(labeledFilePath)
	#mostCommonBigrams(labeledFilePath)
	#mostCommonTrigrams(labeledFilePath)
