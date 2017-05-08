def toProbRowAndCol(D, rowNames, colNames):
	E = { row : { col : 0 for col in colNames } for row in rowNames }
	
	s = 0.0
	for r in D:
		for c in D[r]:
			s += D[r][c]

	for r in D:
		for c in D[r]:
			E[r][c] = D[r][c] / s

	return s

def toProbColGivenRow(D, rowNames, colNames):
	E = { row : { col : 0 for col in colNames } for row in rowNames }
	for r in rowNames:
		s = 0.0
		for c in colNames:
			if r in D and c in D[r]:
				s += D[r][c]

		if s > 0:
			for c in colNames:
				if r in D and c in D[r]:
					E[r][c] = D[r][c] / s
	return E

def toProbRowGivenCol(D, rowNames, colNames):
	E = { row : { col : 0 for col in colNames } for row in rowNames }
	for c in colNames:
		s = 0.0
		for r in rowNames:
			if r in D and c in D[r]:
				s += D[r][c]

		if s > 0:
			for r in rowNames:
				if r in D and c in D[r]:
					E[r][c] = D[r][c] / s
	return E
