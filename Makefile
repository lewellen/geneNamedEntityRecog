.PHONY: tests

tests: test/*.py
	python -m unittest discover
