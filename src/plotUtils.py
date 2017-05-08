import matplotlib.pyplot as plot
import numpy

def plotGroupedBarChart(D, rowNames, colNames, xlabel, ylabel):
	# Create a bar chart where bars representing each row are presented 
	# side-by-side for each column in the nested dictionary D.

	numRows = len(rowNames)
	numCols = len(colNames)

	indices = range(numCols)
	sortedColNames = sorted(colNames)

	colWidth = 0.65
	colOffset = 0.5 * (1.0 - colWidth)
	barWidth = (colWidth / float(len(rowNames)))

	for rowNum, rowName in enumerate(rowNames):
		offsets = [index + colOffset + (rowNum * barWidth) for index in indices]
		sortedValues = [D[rowName][colName] for colName in sortedColNames]
		plot.bar(offsets, sortedValues, label = rowName, width = barWidth)

	offsets = [0.5 + index for index in indices]
	plot.xticks(offsets, sortedColNames, rotation = 90)
	plot.xlabel(xlabel)
	plot.ylabel(ylabel)
	plot.legend(loc = "upper right") 
	plot.show()

def plotStackedBarChart(D, rowNames, colNames, xlabel, ylabel):
	# Create a stacked bar chart where bars represent each row are presentd stacked
	# for each column in the nested dictionary D. Will auto normalize so range is
	# [0,1].

	numCols = len(colNames)

	indices = range(numCols)
	sortedColNames = sorted(colNames)

	prev = numpy.zeros(numCols)
	for rowName in rowNames:
		sortedValues = [ D[rowName][colName] for colName in sortedColNames ]
		plot.bar(indices, sortedValues, label = rowName, bottom = prev, width = 1)
		prev = numpy.add(prev, sortedValues)

	plot.xticks(indices, sortedColNames, rotation = 90)
	plot.xlabel(xlabel)
	plot.ylabel(ylabel)
	plot.legend(loc = "upper right") 
	plot.show()

def plotCorrelMatrix(corr, tags):
	sortedTags = sorted(tags)
	numTags = len(sortedTags)
	indices = range(numTags)

	T = numpy.zeros((numTags, numTags))
	for i, a in enumerate(sortedTags):
		for j, p in enumerate(sortedTags):
			# these indices are swapped so it matches with the chart labels
			T[i, j] = corr[a][p]

	indices = range(numTags)
	indices = [ i + 0.5 for i in indices]

	f, subPlot = plot.subplots(1, 1)

	subPlot.set_xticks(indices)
	subPlot.set_xticklabels(sortedTags, rotation=90)
	subPlot.set_xlabel("Feature")
	subPlot.set_yticks(indices)
	subPlot.set_yticklabels(sortedTags)
	subPlot.set_ylabel("Feature")

	f.colorbar(
		subPlot.pcolormesh(T, cmap=plot.get_cmap('bwr'), vmin=-1, vmax=1), 
		ax=subPlot
		)
	f.tight_layout()

	plot.show()
