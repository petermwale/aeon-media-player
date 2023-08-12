import sys
from sys import platform
from os import environ, mkdir
from os.path import abspath, exists, expanduser, join
from sqlite3 import connect


HOME_DIR = environ["USERPROFILE"] if "win" in platform else expanduser("~")
AEON_DIR = join(HOME_DIR, "aeon")
DB_DIR = join(AEON_DIR, "database")
DATABASE = join(DB_DIR, "user.db")


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path  = abspath(".")

    return join(base_path, relative_path)

def DatabaseFolderExists():
    try:
        if not exists(resource_path(AEON_DIR)):
            mkdir(resource_path(AEON_DIR))
            print("Created dir:", AEON_DIR)
        if not exists(resource_path(DB_DIR)):
            mkdir(resource_path(DB_DIR))
            print("Created dir:", DB_DIR)
    except:
        return
    return True

def PlaylistTableExists():
    try:
        with connect(resource_path(DATABASE)) as db:
            cursor = db.cursor()
            cursor.execute("CREATE TABLE playlists (name text, media text)")
            db.commit()
            print("Created table: playlists")
    except Exception as err:
        print("Error creating table:", err)
    return True

def GetPlaylists():
    try:
        with connect(resource_path(DATABASE)) as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM playlists")
            media = {a:b for a,b in cursor}
            myList = {}
            for a, b in media.items():
                files = [x for x in b.split("?") if exists(x)]
                myList[a] = "?".join(files)
                AddToPlaylist(a, files)
            return myList
    except Exception as err:
        print("Error getting playlists:", err)
        return {}

def CreatePlaylist(playlist_name):
    if DatabaseFolderExists() and PlaylistTableExists():
        try:
            with connect(resource_path(DATABASE)) as db:
                cursor = db.cursor()
                cursor.execute(f"INSERT INTO playlists (name, media) VALUES ('{playlist_name}', '')")
                db.commit()
                print("Created playlist:", playlist_name)
                return True
        except Exception as err:
            print("Error creating playlist:", err)
    return

def RemovePlaylist(playlist_name):
    try:
        with connect(resource_path(DATABASE)) as db:
            cursor = db.cursor()
            cursor.execute(f"DELETE FROM playlists WHERE name = '{playlist_name}'")
            db.commit()
            print("Removed playlist:", playlist_name)
            return True
    except Exception as err:
        print("Error removing playlist:", err)
        return

def RenamePlaylist(playlist_name, new_playlist_name):
    try:
        with connect(resource_path(DATABASE)) as db:
            cursor = db.cursor()
            cursor.execute(f"UPDATE playlists SET name = '{new_playlist_name}' WHERE name = '{playlist_name}'")
            db.commit()
            print(f"Renamed playlist '{playlist_name}' --> '{new_playlist_name}'")
            return True
    except Exception as err:
        print("Error renaming playlist:", err)
        return

def AddToPlaylist(playlist_name, media):
    files = "?".join(media)
    try:
        with connect(resource_path(DATABASE)) as db:
            cursor = db.cursor()
            cursor.execute(f"UPDATE playlists SET media = '{files}' WHERE name = '{playlist_name}'")
            db.commit()
            print(f"Added {len(media)} file(s) to playlist '{playlist_name}'")
            return True
    except Exception as err:
        print("Error adding media file(s) to playlist:", err)
        return