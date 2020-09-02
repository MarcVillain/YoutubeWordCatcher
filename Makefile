CHANNEL=""
WORD=""
API_KEY=""

catch:
	python ymc.py catch $(CHANNEL) $(WORD) $(API_KEY)

format:
	black -l 120 .
