import pytube

import os
import sys
import subprocess
import time

from PySide2 import QtWidgets, QtCore

qt_app = QtWidgets.QApplication(sys.argv)


def convert_video(video_path):
    mp3 = "%s.mp3" % video_path.rstrip(".mp4")
    ffmpeg = ("ffmpeg -i \"%s\" \"%s\" " % (video_path, mp3))
    subprocess.call(ffmpeg, shell=True)

    # remove originally downloaded video
    os.remove(video_path)


def download_playlist(link, dest_path):
    playlist = pytube.Playlist(link)

    # Get files in the destination folder before downloading
    files_in_dest_folder = os.listdir(dest_path)

    playlist.download_all(dest_path)

    # wait a second to ensure last video is ready to convert to mp3
    time.sleep(1)

    # Get files in the destination folder after downloading
    updated_files = os.listdir(dest_path)

    # Fetch file paths of newly downloaded files
    new_files = [
        "%s/%s" % (dest_path, f)
        for f in updated_files
        if f not in files_in_dest_folder
    ]
    # Convert them to mp3
    for new_file in new_files:
        convert_video(new_file)


def download_video(link, dest_path):
    # Get files in the destination folder before downloading
    files_in_dest_folder = os.listdir(dest_path)

    # Download video
    yt = pytube.YouTube(link)

    video = yt.streams.first()
    video.download(dest_path)

    # wait a second to ensure the video is ready to convert to mp3
    time.sleep(1)

    # Get files in the destination folder after downloading
    updated_files = os.listdir(dest_path)
    video_title = "unknown.mp4"
    for _file in updated_files:
        if _file not in files_in_dest_folder:
            video_title = _file

    if video_title != "unknown.mp4":
        convert_video("%s/%s" % (dest_path, video_title))


class YoutubeDownloader(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(YoutubeDownloader, self).__init__(parent)

        self.dest_path = "D:/Simon/Music/"

        # UI Stuff
        self.main_layout = QtWidgets.QVBoxLayout()

        # youtube video input
        self.inputs = QtWidgets.QVBoxLayout()
        self.add_input_field()

        # Display destination folder in UI
        self.path_box = QtWidgets.QHBoxLayout()
        self.path_box_label = QtWidgets.QLabel("Destination Folder: ")
        self.dest_path_ui = QtWidgets.QLineEdit(self.dest_path)
        self.browse_button = QtWidgets.QPushButton("Browse")
        self.download_button = QtWidgets.QPushButton("Download")

        self.path_box.addWidget(self.path_box_label)
        self.path_box.addWidget(self.dest_path_ui)
        self.path_box.addWidget(self.browse_button)
        self.path_box.addWidget(self.download_button)

        self.main_layout.addLayout(self.inputs)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.path_box)

        self.setLayout(self.main_layout)

    def remove_input(self, layout):
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

    def add_input_field(self):
        # new horizontal box for the new items
        input_field_layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("url: ")
        line_edit = QtWidgets.QLineEdit()
        add_button = QtWidgets.QPushButton("Add Link")
        remove_button = QtWidgets.QPushButton("Remove link")

        input_field_layout.addWidget(label)
        input_field_layout.addWidget(line_edit)
        input_field_layout.addWidget(add_button)
        input_field_layout.addWidget(remove_button)

        self.inputs.addLayout(input_field_layout)

        add_button.clicked.connect(self.add_input_field)
        remove_button.clicked.connect(
            lambda: self.remove_input(input_field_layout)
        )

    def run(self):
        # Show the window
        self.show()
        # Run the qt application
        qt_app.exec_()


yt_downloader = YoutubeDownloader()
yt_downloader.run()
