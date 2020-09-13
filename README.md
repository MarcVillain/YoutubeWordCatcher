YoutubeWordCatcher
===

Extract every clip of a Youtube channel's videos where a specific word is pronounced and build a big video out of it.

# Install

```bash
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

# Configure

You can edit the configuration by creating a `config.ini` file.

The available sections are:
* **all** : will be loaded in every configuration
* **command** : will be loaded only for the specified command (example: catch)

You can find all the possible values for the configuration in the `config.py` files located in the `commands` folder.

Note that whenever there are dictionaries or lists, you can represent the data on a multiline but beware of the indentation.

Example `config.ini`:
```ini
[all]
channel_name=AwesomeChannel
word_to_extract=hello

[catch]
api_key=XXX...XX

[chart]
title_colors = {
               "Awesome Game": "red",
               }
```

# Run

In order to run properly, you need to get a Youtube API key, which you can obtain by following the instructions [here](https://developers.google.com/youtube/registering_an_application).

```bash
python ywc.py catch --help
```

> :warning: **If you are using Windows**
>
> You must set the environment variables **FFMPEG_BINARY** and **IMAGEMAGICK_BINARY** or you will get the error "_FileNotFoundError: [WinError 2] The system cannot find the file specified_".

# Chart

To visualize the data generated by this program, I wrote a command to generate charts.

To use it, make sure you generated the data by running the main program, then execute:

```bash
python ymc.py chart --help
```

You can look at the code to edit some variables if necessary, or add your own data visualization.

# Example

A complete example is available in [EXAMPLE.md](EXAMPLE.md).

# Todo

* Manual clip sorter to remove false positives
* Improve timestamps with SpeechRecognition plugin

# Authors

* Marc Villain <marc.villain@epita.fr>
