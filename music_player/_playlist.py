"""Folder scanning for local audio files."""

import os


AUDIO_EXTENSIONS = (
    '.mp3', '.wav', '.flac', '.ogg', '.oga', '.opus',
    '.m4a', '.mp4', '.aac', '.aiff', '.aif',
    '.wma', '.ac3', '.ape', '.dsf', '.dff',
)


def scan_audio_folder(folder_path):
    result = []
    if not folder_path or not os.path.isdir(folder_path):
        return result
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            if f.lower().endswith(AUDIO_EXTENSIONS):
                result.append(os.path.join(root, f))
    result.sort()
    return result