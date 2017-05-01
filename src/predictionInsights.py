import collections
import common
import evaluation
import main
import operator

import numpy
import matplotlib.pyplot as plot

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
	indices = range(len(allKeys))
	indexByKey = { key : index for (key, index) in zip(allKeys, indices) }
	plot.xticks(indices, allKeys, rotation=90)

	for tag in tags:
		tagKeys = sorted(E[tag].keys())
		tagValues = [ E[tag][key] for key in tagKeys ]
		tagIndices = [ indexByKey[key] for key in tagKeys ]
		plot.bar(tagIndices, tagValues, label=tag, alpha=0.5, width=.8)

	plot.yscale('log')
	plot.ylabel("log P(tag | token)")
	plot.xlabel("Token")
	plot.legend(loc="upper right")
	plot.show()

if __name__ == "__main__":
	inputFilePath = "res/genetag.labeled"

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

	tags = sorted( ["I", "O", "B"] )

	unigramConfusion(tags, test, decoded)
	bigramConfusion(tags, test, decoded)

	histInitVecGridStateTrans(corpusStats)
	histEmissionProbs(corpusStats, tags)
