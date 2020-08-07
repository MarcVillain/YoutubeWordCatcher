YoutubeWordCatcher
===

Little script that extracts every clip where a Youtuber says a specific word and builds a big video out of it.

# Install

```bash
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

# Run

In order to run properly, you need to get a Youtube API key, which you can obtain by following the instructions [here](https://developers.google.com/youtube/registering_an_application).

```bash
python ./run.py <api_key> <channel_name> <word>
```

# Authors

* Marc Villain <marc.villain@epita.fr>