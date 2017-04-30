import unittest

from src import evaluation

class ConfusionMatrixTests(unittest.TestCase):
	def test_accuracy(self):
		classes = range(0, 3)
		actuals = [ 0, 1, 2, 0, 1, 2, 0, 1, 2]
		predictions = [0, 1, 0, 0, 0, 2, 0, 1, 0]

		C = evaluation.ConfusionMatrix(classes, actuals, predictions)
		actual = C.accuracy()
		expected = 2.0 / 3.0

		self.assertEqual(actual, expected)

if __name__ == "__main__":
	unittest.main()
