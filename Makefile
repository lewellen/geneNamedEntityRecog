.PHONY: tests clean

tests: test/*.py
	python -m unittest discover

clean:
	rm -rf res/*.labeled
	rm -rf res/*.unlabeled
