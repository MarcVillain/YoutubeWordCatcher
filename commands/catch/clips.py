def list_for(conf, videos):
    counter = 0

    for video in videos:
        video_id = video["id"]["videoId"]
        if len(conf.filter_videos_ids) > 0 and (video_id not in conf.filter_videos_ids):
            continue
        if len(conf.filter_out_videos_ids) > 0 and (video_id in conf.filter_out_videos_ids):
            continue

        if len(video["data"].get("clips", [])) > 0:
            for i, clip in enumerate(video["data"]["clips"]):
                counter += 1
                yield video, clip, i + 1, counter
