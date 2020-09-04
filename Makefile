.PHONY: install catch chart format

install:
	python3 -m venv venv
	source ./venv/bin/activate
	pip install -r requirements.txt

catch:
	python ywc.py catch

chart:
	python ywc.py chart

format:
	black -l 120 .
