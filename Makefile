CHANNEL=""
WORD=""
API_KEY=""

catch:
	python ywc.py catch $(CHANNEL) $(WORD) $(API_KEY)

format:
	black -l 120 .
