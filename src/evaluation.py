import random

import common
import hiddenMarkovModel as hmm

class ConfusionMatrix:
	def __init__(self, classes, actuals, predictions):
		if len(classes) == 0:
			raise Exception("'classes' must have atleast one instance.")

		if len(actuals) != len(predictions):
			raise Exception("'actuals' and 'predictions' must have same number of entries.")

		# Discrete set of domain outcomes (labels, classes, tags, etc)
		self.classes = classes

		# matrix[actual][predicted] = count
		self.matrix = { a : { p : 0 for p in self.classes } for a in self.classes }

		# tally the results based on a list of expected values and predicted values
		for (a, p) in zip(actuals, predictions):
			self.matrix[a][p] += 1

	def accuracy(self):
		# Measure the number of correct predictions (sum_i M[i,i]) / (sum_{i,j} M[i,j})
		n = sum( [ self.matrix[a][a] for a in self.classes] )
		d = sum( [ sum([ self.matrix[a][p] for p in self.classes]) for a in self.classes ] )

		if d == 0:
			raise ZeroDivisionError("Accuracy calculation requires non-zero confusion matrix.")

		return float(n) / float(d)

	def toConsole(self):
		print("\t%s" % " ".join(map(lambda x : str(x), self.classes)))
		for a in self.classes:
			print("%s\t%s" % (
				str(a),
				" ".join([str(self.matrix[a][p]) for p in self.classes])
			))

def kFoldsCrossValidation(K, taggedSentences, smooth, prob):
	trainAcc = []
	testAcc = []

	for _ in range(0, K):
		train, test = splitTrainTest(taggedSentences, 1.0 / K)
		decoder = hmm.TagDecoder(CorpusStatistics(train, smooth), prob)
		trainAcc.append(accuracy(train, decoder))
		testAcc.append(accuracy(test, decoder))

	return (sum(trainAcc) / K, sum(testAcc) / K)

def splitTrainTest(dataset, portion):
	random.shuffle(dataset)

	foldSize = int(len(dataset) * portion)
	train = dataset[foldSize:]
	test = dataset[:foldSize]

	return (train, test)

def accuracy(dataset, decoder):
	count = 0.0
	numRight = 0.0
	n = 0

	for expected in dataset:
		actual = decoder.decode(common.Sentence(expected.toWordSeq()))

		alignment = zip(expected.toTagSeq(), actual.toTagSeq())
		count += len(alignment)
		numRight += len(filter(lambda (e,a): e == a, alignment))

		n += 1
		if n > 100:
			break

	return numRight / count

