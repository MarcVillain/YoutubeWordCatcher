import sys

from api import YoutubeAPI

if len(sys.argv) < 4:
    print("usage: ./run.py <api_key> <channel_name> <word>")
    exit(1)

api_key = sys.argv[1]
channel_name = sys.argv[2]
word_to_extract = sys.argv[3]

api = YoutubeAPI(api_key)
