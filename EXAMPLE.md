YoutubeWordCatcher - Example
===

This example showcases the use of the script on [EthosLab's Youtube channel](https://www.youtube.com/channel/UCFKDEp9si4RmHFWJW1vYsMA) and on the word "**actually**".

# Configuration file

```ini
[all]
channel_name=EthosLab
word_to_extract=actually
# Used this for stats command and words chart:
# word_to_extract=.+

[catch]
api_key=***hidden***
max_data_thread_workers=4

[chart]
title_colors = {
               "Etho Plays Minecraft": "red",
               "Pixelmon": "green",
               "Hermit": "orange",
               "TerraFirma": "pink",
               "ARK Survival": "cyan",
               "Ozone": "purple",
               "Modded": "yellow",
               "Terraria": "brown",
               "Sky Factory": "grey",
               "Diversity": "blue",
               }
words_chart_words_color = {
                          "actually": "red",
                          }
words_chart_max_words_display_count=200
```

# Generated video

[Etho (feat. friends) - actually](https://www.youtube.com/channel/UCFKDEp9si4RmHFWJW1vYsMA)

[![Etho (feat. friends) - actually](https://i9.ytimg.com/vi/mr89gFoqylo/hqdefault.jpg?sqp=CLzg9foF&rs=AOn4CLDvUEqzQU36zKDFTAE_yqY6SgztlA)](https://www.youtube.com/watch?v=mr89gFoqylo "Etho (feat. friends) - actually")

# Charts

| ![Amount of 'actually' per video](images/example_chart_amount.jpg?raw=True "") | ![Average amount of 'actually' per second, per video](images/example_chart_average.jpg?raw=True "Average amount of 'actually' per second, per video") |
|:--:|:--:|
| Type: amount | Type: average |
| *Amount of 'actually' per video* | *Video's types repartition* |

| ![Video's types repartition](images/example_chart_color.jpg?raw=True "Video's types repartition") | ![Words usage](images/example_chart_words.jpg?raw=True "Words usage") |
|:--:|:--:|
| Type: words | Type: color |
| *Words usage* | *Video titles repartition* |

# Stats

```bash
...
> Compute statistics
> ===================== Statistics =====================
> Number of videos: 1478
> Number of words: 3141416
> First 10 words: I (109250 times), the (94599 times), to (77281 times), a (68073 times), it (67626 times), and (63477 times), you (51727 times), this (50688 times), we (49676 times), so (47783 times)
actually >> Amount: 6718
actually >> Position: 89
actually >> Average per video: 0.002138526065952424
actually >> Most amount in a video: 42 times in 'Etho Plays Minecraft - Episode 500: LP World Tour'
actually >> Most per seconds in a video: every 59.11357142857143 second times in 'Minecraft - TerraFirmaPunk #10: Spruce Sluice'
actually >> Most per word in a video: every 140.76470588235293 word in 'Let&#39;s Play Minecraft - Episode 33: Beta 1.3'
```

