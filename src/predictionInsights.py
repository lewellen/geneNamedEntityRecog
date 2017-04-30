import collections
import common
import evaluation
import main

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


if __name__ == "__main__":
	inputFilePath = "res/genetag.labeled"

	trainFilePath = "train.labeled.txt"
	testFilePath = "test.labeled.txt"
	unlabeledFilePath = "test.unlabeled.txt"
	decodedFilePath = "test.decoded.txt"

	main.createTrainTest(inputFilePath, trainFilePath, testFilePath)
	main.removeTags(testFilePath, unlabeledFilePath)
	main.decode(trainFilePath, unlabeledFilePath, decodedFilePath)

	fileFormat = common.LabeledFormat()
	test = list(fileFormat.deserialize(testFilePath))
	decoded = list(fileFormat.deserialize(decodedFilePath))

	tags = sorted( ["I", "O", "B"] )


	unigramConfusion(tags, test, decoded)
	bigramConfusion(tags, test, decoded)
