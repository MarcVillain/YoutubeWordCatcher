CHANNEL=""
WORD=""

catch:
	python ymc.py catch $(CHANNEL) $(WORD)

format:
	black -l 78 *.py **/*.py
