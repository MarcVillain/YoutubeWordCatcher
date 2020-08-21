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

You can edit the configuration in the `config.py` file.

```bash
python ./run.py
```

# TODO

* Multithread the data extraction
* Manual clip sorter to remove false positives

# Authors

* Marc Villain <marc.villain@epita.fr>