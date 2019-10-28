import pytube

import os
import sys
import subprocess
import time
import re

from PySide2 import QtWidgets, QtCore, QtGui


def convert_video(video_path):
    mp3 = "%s.mp3" % video_path.rstrip(".mp4")
    ffmpeg = ("ffmpeg -i \"%s\" \"%s\" " % (video_path, mp3))
    subprocess.call(ffmpeg, shell=True)

    # remove originally downloaded video
    os.remove(video_path)


def download_playlist(link, dest_path, ext):
    playlist = pytube.Playlist(link)

    if ext == "mp3":
        # Get files in the destination folder before downloading
        files_in_dest_folder = os.listdir(dest_path)

    playlist.download_all(dest_path)

    if ext == "mp3":
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


def download_video(link, dest_path, ext):
    if ext == "mp3":
        # Get files in the destination folder before downloading
        files_in_dest_folder = os.listdir(dest_path)

    # Download video
    yt = pytube.YouTube(link)

    video = yt.streams.first()
    video.download(dest_path)

    if ext == "mp3":
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

        self.setWindowTitle("youtube downloader")

        self.dest_path = "D:/Simon/Music/"
        self.feedback = []

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

        self.browse_button.clicked.connect(self.browse)
        self.download_button.clicked.connect(self.prepare_download)

    def browse(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setDirectory(self.dest_path)
        file_dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)

        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.dest_path = file_dialog.selectedUrls()[0].toString().strip("file:///")

        self.dest_path_ui.setText(self.dest_path)

    def prepare_download(self):
        # init lists that will store all urls
        # using dict I can also make sure
        # there is only ever one entry for a given link
        url_dict = {
            "videos": {},
            "playlists": {}
        }

        # Process inputs
        for layout in self.inputs.children():
            for i in range(layout.count()):
                # Get line edits (aka urls)
                if type(layout.itemAt(i).widget()) == QtWidgets.QLineEdit:
                    url = layout.itemAt(i).widget().text()
                # Get checkbox
                if type(layout.itemAt(i).widget()) == QtWidgets.QCheckBox:
                    ext = "mp3" if layout.itemAt(i).widget().isChecked() else "mp4"

            # add url to the right list
            if "playlist" in url:
                url_dict["playlists"][url] = ext
            else:
                url_dict["videos"][url] = ext

        # download videos
        for video in url_dict["videos"].keys():
            try:
                download_video(
                    video,
                    self.dest_path,
                    url_dict["videos"][video]
                )
                self.feedback.append(
                    "%s downloaded to %s" % (video, self.dest_path)
                )
            except Exception as error:
                self.feedback.append(
                    "%s failed to download\n(%s)" % (video, error)
                )

        # download playlists
        for playlist in url_dict["playlists"].keys():
            try:
                download_playlist(
                    playlist,
                    self.dest_path,
                    url_dict["playlists"][playlist]
                )
                self.feedback.append(
                    "%s downloaded to %s" % (video, self.dest_path)
                )
            except Exception as error:
                self.feedback.append(
                    "%s failed to download (%s)" % (video, error)
                )

        feedback_box = QtWidgets.QMessageBox()

        feedback_box.setWindowTitle("Feedback")
        feedback_box.setText("\n\n".join(self.feedback))

        feedback_box.exec_()
        self.close()

    def remove_input(self, layout):
        if len(self.inputs.children()) > 1:
            layout.setParent(None)
            for i in reversed(range(layout.count())):
                layout.itemAt(i).widget().setParent(None)

    def add_input_field(self):
        # new horizontal box for the new items
        input_field_layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("url: ")
        line_edit = QtWidgets.QLineEdit()
        extention = QtWidgets.QCheckBox(".mp3")
        add_button = QtWidgets.QPushButton("Add Link")
        remove_button = QtWidgets.QPushButton("Remove link")

        input_field_layout.addWidget(label)
        input_field_layout.addWidget(line_edit)
        input_field_layout.addWidget(extention)
        input_field_layout.addWidget(add_button)
        input_field_layout.addWidget(remove_button)

        self.inputs.addLayout(input_field_layout)

        add_button.clicked.connect(self.add_input_field)
        remove_button.clicked.connect(
            lambda: self.remove_input(input_field_layout)
        )


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = YoutubeDownloader()
    main.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
