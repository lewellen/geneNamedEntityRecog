import collections
import operator
import math
import sys

import common
import evaluation
import main
import binaryResponse
import plotUtils

import numpy
import matplotlib.pyplot as plot

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

def interpretConfusion(stringList, stringLabels):
	vectorizer = CountVectorizer(stop_words = None)
	termDocumentMatrix = vectorizer.fit_transform(stringList)

	model = LogisticRegression()
	model.fit(termDocumentMatrix, stringLabels)

	indexToVocab = { index : word for (word, index) in vectorizer.vocabulary_.items() }
	coefByVocab = { word : model.coef_[0, vectorizer.vocabulary_[word]] for word in vectorizer.vocabulary_ }

	return sorted(coefByVocab.items(), key=operator.itemgetter(1))

def plotLogConfusionMatrix(confusion, tags):
	sortedTags = sorted(tags)
	numTags = len(sortedTags)
	indices = range(numTags)

	T = numpy.zeros((numTags, numTags))
	for a in indices:
		for p in indices:
			# these indices are swapped so it matches with the chart labels
			T[a, p] = math.log(1 + sum(confusion[sortedTags[a]][sortedTags[p]].values()))

	indices = range(numTags)
	indices = [ i + 0.5 for i in indices]

	f, subPlot = plot.subplots(1, 1)

	subPlot.set_xticks(indices)
	subPlot.set_xticklabels(sortedTags)
	subPlot.set_xlabel("Predicted Label")
	subPlot.set_yticks(indices)
	subPlot.set_yticklabels(sortedTags)
	subPlot.set_ylabel("Actual Label")

	f.colorbar(subPlot.pcolormesh(T), ax=subPlot)
	f.tight_layout()

	plot.show()

def unigramConfusion(tags, test, decoded):
	confusion = { a : { p : collections.Counter() for p in tags } for a in tags }
	for (T, D) in zip(test, decoded):
		for (t, d) in zip(T.taggedWords, D.taggedWords):
			confusion[t.tag][d.tag].update([t.word])

	print("Actual Predicted\tMost common words")
	for a in tags:
		if a == "O":
			# Overabundance of outside tags - more meaningful to focus on begin and 
			# inside tags.
			continue

		for p in tags:
			if a == p:
				# For the purpose of this plot, care about mismatches
				continue

			print("%s %s:\t" % (a, p)),
			mostCommon = map(lambda (s, n): "(%d) \"%s\"" % (n, s), confusion[a][p].most_common(10))
			print("%s" % ", ".join(mostCommon))


	maxCount = 0
	am, pm = None, None
	for a in tags:
		for p in tags:
			if a == p:
				continue

			count = sum(confusion[a][p].values())
			if maxCount < count:
				maxCount = count
				am, pm = a, p

	mostConfused = confusion[am][pm].most_common(5)

	words = { word : [] for (word, count) in mostConfused }
	labels = { word : [] for (word, count) in mostConfused }

	for taggedSentence in test:
		for (prev, curr, nex) in zip(taggedSentence.taggedWords, taggedSentence.taggedWords[1:], taggedSentence.taggedWords[2:]):
			for word, count in mostConfused:
				if curr.word == word:
					trigram = "%s" % (prev.word)
					words[curr.word].append(trigram)
					labels[curr.word].append(curr.tag)

	print ("Possible descriminators for eliminating most confused unigrams")
	for (word, count) in mostConfused:
		print ("\"%s\" actual: %s predicted: %s; surrounding words:" % (word, am, pm))
		coefsByWords = interpretConfusion(words[word], labels[word])
		print { k : round(v, 3) for (k, v) in coefsByWords[:5] }
		print { k : round(v, 3) for (k, v) in coefsByWords[-5:] }
		print '----------------------------------------------'

	plotLogConfusionMatrix(confusion, tags)

def bigramConfusion(tags, test, decoded):
	tags = [ "%s%s" % (a, b) for a in tags for b in tags ]

	confusion = { a : { p : collections.Counter() for p in tags } for a in tags }

	for (T, D) in zip(test, decoded):
		for ( (u, a), (v, b) ) in zip(zip(T.taggedWords, D.taggedWords), zip(T.taggedWords[1:], D.taggedWords[1:])):
			t = "%s%s" % (u.tag, v.tag)
			d = "%s%s" % (a.tag, b.tag)
			w = "%s %s" % (u.word, v.word)

			confusion[t][d].update([w])

	print("Actual Predicted\tMost common words")
	for a in tags:
		for p in tags:
			if a == p:
				# For the purpose of this plot, care about mismatches
				continue

			if not confusion[a][p]:
				continue

			print("%s %s:\t" % (a, p)),
			mostCommon = map(lambda (s, n): "(%d) \"%s\"" % (n, s), confusion[a][p].most_common(10))
			print("%s" % ", ".join(mostCommon))

	plotLogConfusionMatrix(confusion, tags)

def histInitVecGridStateTrans(corpusStats):
	tags = corpusStats.initVec.keys()
	sortedTags = sorted(tags)
	numTags = len(sortedTags)
	
	sortedPi = [ corpusStats.initVec[k] for k in sortedTags ]
	T = numpy.zeros((numTags, numTags))

	indices = range(numTags)
	for a in indices:
		for p in indices:
			# these indices are swapped so it matches with the chart labels
			T[p, a] = corpusStats.stateTrans[sortedTags[a]][sortedTags[p]]

	f, subPlots = plot.subplots(1, 2)

	subPlots[0].bar(indices, sortedPi, width=1)
	subPlots[0].set_xticks(indices)
	subPlots[0].set_xticklabels(sortedTags)
	subPlots[0].set_xlabel("Tag")
	subPlots[0].set_ylabel("P($q_0$ = tag)")

	# Want to center the labels so shift indices to the right half a unit
	indices = [ i + 0.5 for i in indices]

	#subPlots[1].imshow(T, origin="lower")
	subPlots[1].set_xticks(indices)
	subPlots[1].set_xticklabels(sortedTags)
	subPlots[1].set_xlabel("Tag")
	subPlots[1].set_yticks(indices)
	subPlots[1].set_yticklabels(sortedTags)
	subPlots[1].set_ylabel("Next Tag")

	f.colorbar(subPlots[1].pcolormesh(T), ax=subPlots[1])
	f.tight_layout()

	plot.show()

def histEmissionProbs(corpusStats, tags):
	E = corpusStats.wordGivenTag

	# Get all the unique keys in ascending order
	allKeys = sorted(list(set([ key for tag in tags for key in E[tag] ])))

	plotUtils.plotGroupedBarChart(
		E, tags, allKeys, "Token", "P(token | tag)"
	)

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print ("%s <res/file.labeled>" % sys.argv[0])
		exit(1)

	inputFilePath = sys.argv[1]

	trainFilePath = "train.labeled.txt"
	testFilePath = "test.labeled.txt"
	unlabeledFilePath = "test.unlabeled.txt"
	decodedFilePath = "test.decoded.txt"

	main.createTrainTest(inputFilePath, trainFilePath, testFilePath)
	main.removeTags(testFilePath, unlabeledFilePath)
	corpusStats = main.decode(trainFilePath, unlabeledFilePath, decodedFilePath)

	fileFormat = common.LabeledFormat()
	test = list(fileFormat.deserialize(testFilePath))
	decoded = list(fileFormat.deserialize(decodedFilePath))

	tags = sorted( ["I", "O"] )

	unigramConfusion(tags, test, decoded)
	bigramConfusion(tags, test, decoded)

	histInitVecGridStateTrans(corpusStats)
	histEmissionProbs(corpusStats, tags)
