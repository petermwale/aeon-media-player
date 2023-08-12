import sys
from os import listdir, remove, mkdir
from os.path import join, split, exists, abspath
from eyed3 import load as loadAudioFile
#from mutagen import File as AudioFile


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path  = abspath(".")

    return join(base_path, relative_path)


def getTrackInfo(track):
    artist = "Unkown artist"
    album = "Unkown album"
    title = split(track)[1]
    
    try:
        audio = loadAudioFile(track)
        artist = audio.tag.artist
        album = audio.tag.album
        title = audio.tag.title
    except Exception as err:
        print("ERROR:", err)
        
    if artist is None:
        artist = "Unkown artist"
    if album is None:
        album = "Unkown album"
    if title is None:
        title = split(track)[1]
        
    return artist, album, title, 0#AudioFile(track).info.length

def getAlbumArt(track):
    if not exists(resource_path("./././data/image/art/")):
        mkdir(resource_path("./././data/image/art/"))
    for art in listdir(resource_path("./././data/image/art/")):
        remove(join(resource_path("./././data/image/art/"), art))
    try:
        audio = loadAudioFile(track)
        for image in audio.tag.images:
            with open(resource_path("./././data/image/art/FRONT_COVER.JPG"), "wb") as fh:
                fh.write(image.image_data)
                print("Wrote album art")
        if len(listdir(resource_path("./././data/image/art/"))) > 0:
            return resource_path( "./././data/image/art/FRONT_COVER.JPG")
        else:
            path = split(track)[0]
            for name in listdir(path):
                if name.lower().endswith((".jpg", ".png")) and ("folder" in name.lower() or \
                    "large" in name.lower() or "small" in name.lower()):
                    with open(resource_path(f"data/image/art/{name}"), "wb") as fh:
                        fh.write(open(join(path, name), "rb").read())
                        print("Wrote album art")
                        return resource_path(f"data/image/art/{name}")
            return resource_path( "./././data/image/album-art.png")
    except Exception as err:
        print("Error loading album art:", err)
        return resource_path("./././data/image/album-art.png")
