def list_for(videos, filter_videos_ids=None, filter_out_videos_ids=None, var="clips"):
    if filter_videos_ids is None:
        filter_videos_ids = []
    if filter_out_videos_ids is None:
        filter_out_videos_ids = []

    counter = 0

    for video in videos:
        video_id = video["id"]["videoId"]
        if len(filter_videos_ids) > 0 and (video_id not in filter_videos_ids):
            continue
        if len(filter_out_videos_ids) > 0 and (video_id in filter_out_videos_ids):
            continue

        values = video.get("data", {}).get(var, [])

        for i, value in enumerate(values):
            counter += 1
            yield video, value, i + 1, counter
