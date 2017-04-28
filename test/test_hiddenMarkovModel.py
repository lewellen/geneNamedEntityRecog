import unittest

from src import common
from src import hiddenMarkovModel as hmm

class TestHmmHistogram(unittest.TestCase):
	def test_toDistribution(self):
		H = hmm.Histogram()

		for i in xrange(0, 10):
			for j in xrange(0, i):
				H.observe([i])

		actual = H.toDistribution()
		expected = { i :  float(i) / 45.0  for i in xrange(1, 10) } 	

		self.assertEqual(actual, expected)

class TestHmmCorpusStatistics(unittest.TestCase):
	def test_InitWithoutSmoothing(self):
		words = "the quick brown fox.".split()
		tags = ["O", "B", "I", "O"]
		taggedSentence = common.TaggedSentence( [
			common.TaggedWord(word, tag) for (word, tag) in zip(words, tags)
			] )

		# Disable lapace smoothing
		taggedSentences = [ taggedSentence ]
		corpusStats = hmm.CorpusStatistics(taggedSentences, useSmoothing=False)

		# initial state prob:  p(q_0)
		expectedInitVec = { "O" : 1 }
		self.assertEqual(corpusStats.initVec, expectedInitVec)

		# Transition prob: P(q | q_prev )
		expectedStateTrans = {
			"O" : { "B" : 1 },
			"B" : { "I" : 1 },
			"I" : { "O" : 1 }
		}
		self.assertEqual(corpusStats.stateTrans, expectedStateTrans)

		# Emission prob: P(w | q)
		expectedWordGivenTag = {
			"O" : { "the" : 0.5, "fox." : 0.5 },
			"B" : { "quick" : 1 },
			"I" : { "brown" : 1 }
		}

		self.assertEqual(corpusStats.wordGivenTag, expectedWordGivenTag)

	def test_InitWithSmoothing(self):
		words = "the quick brown fox.".split()
		tags = ["O", "B", "I", "O"]
		taggedSentence = common.TaggedSentence( [
			common.TaggedWord(word, tag) for (word, tag) in zip(words, tags)
			] )

		# Laplace smoothing enabled, add dummy counts to all states
		taggedSentences = [ taggedSentence ]
		corpusStats = hmm.CorpusStatistics(taggedSentences, useSmoothing=True)

		# initial state prob:  p(q_0)
		expectedInitVec = { "O" : 0.5, "B" : 0.25, "I" : 0.25 }
		self.assertEqual(corpusStats.initVec, expectedInitVec)

		# Transition prob: P(q | q_prev )
		expectedStateTrans = {
			"O" : { "O" : 0.25, "B" : 0.5, "I" : 0.25 },
			"B" : { "O" : 0.25, "B" : 0.25, "I" : 0.5 },
			"I" : { "O" : 0.5, "B": 0.25, "I" : 0.25 }
		}
		self.assertEqual(corpusStats.stateTrans, expectedStateTrans)

		# Emission prob: P(w | q)
		expectedWordGivenTag = {
			"O" : { "the" : 0.5, "fox." : 0.5 },
			"B" : { "quick" : 1 },
			"I" : { "brown" : 1 }
		}

		self.assertEqual(corpusStats.wordGivenTag, expectedWordGivenTag)

class TestHmmTagDecoder(unittest.TestCase):
	def test_decode(self):
		iceCreamModel = hmm.CorpusStatistics([])

		iceCreamModel.States = { "COLD": 1, "HOT": 2 }
		iceCreamModel.Indices = { 1: "COLD", 2: "HOT" }
		iceCreamModel.initVec = { "COLD": 0.2, "HOT": 0.8 }
		iceCreamModel.stateTrans = { 
			"COLD" : { "HOT": 0.4, "COLD": 0.6 },
			"HOT" : { "HOT": 0.7, "COLD": 0.3 }
		}
		iceCreamModel.wordGivenPOS = {
			"COLD": { "1": 0.5, "2": 0.4, "3": 0.1 },
			"HOT": { "1": 0.2, "2": 0.4, "3": 0.4 }
		}

		decoder = hmm.TagDecoder(iceCreamModel)
		tagged = decoder.decode(common.Sentence(["3", "1", "3"]))
		self.assertEqual(tagged.toTagSeq(), ["HOT", "HOT", "HOT"])

if __name__ == "__main__":
	unittest.main() 
