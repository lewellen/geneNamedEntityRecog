import collections
import math

class LogisticRegression:
	def __init__(self):
		self.labels = []
		self.wordWeights = collections.defaultdict(float)
		self.bias = 0

	def fit(self, wordList, labelList, learnRate = 1.0, regFactor = 0.25, maxIter = 10):
		assert len(wordList) > 0
		assert len(wordList) == len(labelList)
		assert learnRate > 0
		assert regFactor >= 0

		uniqueLabels = self.__getUnique(labelList)
		assert len(uniqueLabels) == 2
		self.labels = uniqueLabels

		uniqueWords = self.__getUnique(wordList)

		self.bias = 0
		self.wordWeights = { word : 0 for word in uniqueWords }

		# Learning rate
		eta = learnRate

		# regularization term
		mu = regFactor

		wordsByLabel = { label.lower() : collections.Counter() for label in uniqueLabels }
		for (word, label) in zip(wordList, labelList):
			wordsByLabel[label.lower()].update([word.lower()])

		for iteration in xrange(0, maxIter):
			for labelIndex in [0, 1]:
				p = self.__calcPi(self.bias, self.wordWeights, wordsByLabel[uniqueLabels[0]])

				self.bias += eta * (labelIndex - p)
				self.bias *= (1.0 - 2.0 * eta * mu)

				for (word, count) in wordsByLabel[uniqueLabels[labelIndex]].items():
					self.wordWeights[word] += eta * (labelIndex - p) * count
					self.wordWeights[word] *= (1.0 - 2.0 * eta * mu)

	def predict(self, wordList):
		pi = self.__calcPi(self.bias, self.wordWeights, collections.Counter(wordList))
		return { self.labels[0] : 1 - pi, self.labels[1] : pi }

	def __calcPi(self, B0, B, N):
		# w0 is scalar floating bias
		# B is dictionary { scalar string word : scalar floating weight }
		# N is Counter { scalar string word : scalar integer count }
		p = sum( [ N[w] * B[w] for w in B ] )
		p = math.exp(B0 - p)
		p = p / (1.0 + p)

		return p

	def __getUnique(self, stringList):
		return list(set(map(lambda x : x.lower(), filter(lambda x: not x is None, stringList))))
