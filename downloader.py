import pytube

import os
import subprocess
import time

with open("./data/links.txt") as links:
    links = [link.rstrip("\n") for link in links.readlines()]

dest_path = "D:/Simon/Music"
for link in links:
    print("Processing %s" % link)

    # Get files in the destination folder before downloading
    files_in_dest_folder = os.listdir(dest_path)
    print(files_in_dest_folder)

    # Download video
    yt = pytube.YouTube(link)

    video = yt.streams.first()
    video.download(dest_path)

    time.sleep(1)

    # Get files in the destination folder after downloading
    updated_files = os.listdir(dest_path)
    video_title = "unknown.mp4"
    for _file in updated_files:
        if _file not in files_in_dest_folder:
            video_title = _file

    if video_title != "unknown.mp4":
        mp4 = "%s/%s" % (dest_path, video_title)
        mp3 = "%s.mp3" % mp4.rstrip(".mp4")
        ffmpeg = ("ffmpeg -i \"%s\" \"%s\" " % (mp4, mp3))
        subprocess.call(ffmpeg, shell=True)

        os.remove(mp4)
