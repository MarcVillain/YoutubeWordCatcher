import sys

from api import YoutubeAPI

if len(sys.argv) < 4:
    print("usage: ./run.py <api_key> <channel_name> <word>")
    exit(1)

api_key = sys.argv[1]
channel_name = sys.argv[2]
word_to_extract = sys.argv[3]

api = YoutubeAPI(api_key)

print("> Get channel ID")
search_results = api.search(
    max_results_count=1,
    q=channel_name,
    part="snippet,id",
    type="channel",
    maxResults="1",
)
channel_id = search_results[0]["id"]["channelId"]
