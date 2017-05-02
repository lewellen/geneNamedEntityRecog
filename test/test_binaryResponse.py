import unittest

from src import binaryResponse

class LogisticRegressionTest(unittest.TestCase):
	def test_predict(self):
		model = binaryResponse.LogisticRegression()
		model.bias = 0.0
		model.wordWeights = {
			"no": 0.7,
			"second-rate": 0.9,
			"enjoy": -0.8,
			"great": 1.9
		}
		model.labels = [ "1", "0" ]

		text = "there are virtually no surprises and the writing is second-rate So why did I enjoy it so much? For one thing the case is great"
		p = model.predict(text.split())

		self.assertAlmostEqual(p["1"], 0.94, 2)
		self.assertAlmostEqual(p["0"], 0.06, 2)

	def test_fit(self):
		model = binaryResponse.LogisticRegression()
		model.fit(
			["A", "A", "A", "A", "B", "B", "B", "C", "B", "C", "C", "C", "D", "D", "D", "D" ],
			["1", "1", "1", "1", "1", "1", "1", "1", "0", "0", "0", "0", "0", "0", "0", "0" ],
			learnRate = 1.0, regFactor = .25, maxIter = 1
			)

		p = model.predict(["A"])

		self.assertAlmostEqual(p["1"], 0.53, 2)
		self.assertAlmostEqual(p["0"], 0.47, 2)

if __name__ == "__main__":
	unittest.main()
