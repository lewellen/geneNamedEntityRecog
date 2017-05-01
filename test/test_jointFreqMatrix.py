import unittest

from src import jointFreqMatrix

class JointFreqMatrixTests(unittest.TestCase):
	def test_toProbColGivenRow(self):
		rows = [ "A", "B" ]
		cols = [ "A", "B" ]
		D = { "A": { "A" : 1, "B" : 2 }, "B" : { "A": 3, "B": 4 } }

		A = jointFreqMatrix.toProbColGivenRow(D, rows, cols)
		E = { "A": { "A" : 1/3.0, "B" : 2/3.0 }, "B" : { "A": 3/7.0, "B": 4/7.0 } }

		self.assertEqual(E, A)

	def test_toProbRowGivenCol(self):
		rows = [ "A", "B" ]
		cols = [ "A", "B" ]
		D = { "A": { "A" : 1, "B" : 2 }, "B" : { "A": 3, "B": 4 } }

		A = jointFreqMatrix.toProbRowGivenCol(D, rows, cols)
		E = { "A": { "A" : 1/4.0, "B" : 2/6.0 }, "B" : { "A": 3/4.0, "B": 4/6.0 } }

		self.assertEqual(E, A)

if __name__ == "__main__":
	unittest.main()
