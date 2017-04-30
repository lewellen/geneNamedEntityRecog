
def toProbColGivenRow(D, rowNames, colNames):
	E = D
	for r in rowNames:
		s = 0.0
		for c in colNames:
			s += E[r][c]

		if s > 0:
			for c in colNames:
				E[r][c] /= s
	return E

def toProbRowGivenCol(D, rowNames, colNames):
	E = D
	for c in colNames:
		s = 0.0
		for r in rowNames:
			s += E[r][c]

		if s > 0:
			for r in rowNames:
				E[r][c] /= s
	return E
