import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, 'static', 'media')

SAVE_DIR = MEDIA_DIR

def join_path(directory, filename):
    filepath = os.path.join(directory, filename)
    return filepath