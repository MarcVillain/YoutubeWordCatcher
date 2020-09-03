from matplotlib import pyplot

from utils import charts, logger


def compute(conf, videos):
    x_tags, x_vals, x_colors = [], [], []

    logger.info("Compute the data")
    for video in videos:
        video_id = video["id"]["videoId"]
        video_title = video["snippet"]["title"]
        video_date = video["snippet"]["publishedAt"]
        timestamps = video["data"]["timestamps"]
        color = charts.pick_color(conf.title_colors, video_title)

        x_tags.append(f"{video_date} ({video_id})")
        x_vals.append(len(timestamps))
        x_colors.append(color)

    logger.info("Sort the results")
    # Sort by tags
    x_tags, x_vals, x_colors = zip(*sorted(zip(x_tags, x_vals, x_colors)))

    logger.info("Build the chart")
    x_tags = charts.apply_spacing(x_tags, conf.tag_spacing)
    charts.generate_color_legend(conf.title_colors)
    charts.plot_bar(x_vals, x_tags, x_colors)

    # Export the chart
    if conf.do_output_file:
        chart_file_path = charts.save(f"{conf.channel_name}_amount_of_{conf.word_to_extract}_", conf.charts_folder)
        logger.info(f"Chart saved at: {chart_file_path}")

    # Display the chart
    if conf.do_display_chart:
        logger.info("Display the chart")
        pyplot.show()
