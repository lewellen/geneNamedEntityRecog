.PHONY: data insights tests clean

data:
	python src/genetagToStandard.py
	python src/geniaToStandard.py

insights:
	# make insights corpus=res/foo.labeled
	python src/corpusInsights.py $(corpus)
	python src/predictionInsights.py $(corpus)

tests: test/*.py
	python -m unittest discover

clean:
	rm -rf *.txt
	rm -rf res/*.labeled
	rm -rf res/*.unlabeled
