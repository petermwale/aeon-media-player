import sys
from threading import Thread
from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showinfo
from os import listdir, system, environ, remove
from os.path import join, isfile, expanduser, exists, abspath
from sys import platform
from sqlite3 import connect

if "win" in platform:
    from wmi import WMI

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path  = abspath(".")

    return join(base_path, relative_path)

def isAudio(file):
    return isfile(file) and file.lower().endswith((".mp3", ".wav", ".amr", ".m4a", ".mid", ".ogg", ".aac"))
    
def isVideo(file):
    return isfile(file) and file.lower().endswith((".mp4", ".flv", ".mkv", ".avi", ".mpg"))

def create():
    try:
        with connect(resource_path("data/cryptic/playlist.db")) as db:
            cursor = db.cursor()
            cursor.execute("""CREATE TABLE media (src text, kind text)""")
            db.commit()
        print("Database created successfully!")
    except Exception as err:
        print("Error accessing database:", err)

def get(typ="folder"):
    media = folders = []
    try:
        with connect(resource_path("data/cryptic/playlist.db")) as db:
            cursor = db.cursor()
            cursor = db.execute(f"""SELECT * FROM media""")
        files = [x for x in cursor]
        folders = [x[0] for x in files if x[1] == "folder"]
        media = [x[0] for x in files if x[1] == "media"]
    except Exception as err:
        print("Error getting data from database:", err)
    return media if typ == "media" else folders

def load():
    global listBox, mediaList
    try:
        listBox.delete(0, END)
    except:
        pass
    mediaList.clear()
    for index, folder in enumerate(get()):
        listBox.insert(index, folder)
        mediaList.append(folder)

def add(obj=None, typ="folder", show=True):
    global mediaList
    if show:
        obj = askdirectory()
        if len(obj) <=0 or obj in get():
            return
    try:
        with connect(resource_path("data/cryptic/playlist.db")) as db:
            cursor = db.cursor()
            cursor.execute(f"""INSERT INTO media (src, kind) VALUES ('{obj}', '{typ}')""")
            
            db.commit()
        print(f"Wrote media '{obj}' database successfully!")
        if show:
            load()
    except Exception as err:
        print("Error writing data to database:", err)

def delete(obj=None, typ="folder", show=True):
    if obj is None:
        try:
            obj = listBox.selection_get()
        except:
            return
    try:
        with connect(resource_path("data/cryptic/playlist.db")) as db:
            cursor = db.cursor()
            cursor.execute(f"""DELETE FROM media WHERE src = '{obj}' AND kind = '{typ}'""")
            db.commit()
        print(f"Deleted media '{obj}' from database successfully!")
        if show:
            load()
    except Exception as err:
        print(f"Error deleting media '{obj}' from database:", err)

def scan():
    global scanMyPC

    for folder in get():
        if not exists(folder):
            delete(folder, show=False)
    
    def walk(path):
        global mediaList
        files = [] 
        try:
            for name in listdir(path):
                system("cls" if "win" in platform else "clear")
                print(f"Scanning for media files in '{path}'")
                obj = join(path, name)
                if isfile(obj):
                    if isAudio(obj) or isVideo(obj):
                        files.append(obj)                              
                        mediaList.append(obj)
                else:
                    files.extend(walk(obj))
        except Exception as err:
            print("ERROR:", err)
        return files
    
    path = get()
    
    if not get() and not scanMyPC.get():
        try:
            remove(resource_path("data/cryptic/playlist.db"))
            create()
        except:
            pass
    
    if scanMyPC.get():
        if "win" in platform:
            path = [x.Caption for x in WMI().Win32_LogicalDisk()]
        elif "linux" in platform:
            path = ["/"]
        elif "darwin" in platform:
            path = [join("/Volumes", x) for x in listdir("/Volumes")]
            
    mediaList = []

    def go(path):
        for folder in path:
            for media in walk(folder):
                if media not in get(typ="media"):
                    add(media, "media", False)
                    mediaList.append(media)
                    #print(f"Added media '{media}' to database successfully!")
        print("\n")    
        print("Found", len(mediaList), "media file(s) in your PC.")
        
    t = Thread(go(path), daemon=True)
    t.start()
    t.join()
    
def switch():
    if scanMyPC.get():
        showinfo("Media Manager", "This will take longer, Relax (:-")

def main():
    global mediaList, listBox, scanMyPC
    mediaList = []
    win = Tk()
    win.title("Aeon Media Manager")
    win.geometry("%dx%d+%d+%d" % (600, 400, win.winfo_screenwidth() // 2 - 300, win.winfo_screenheight() // 2 - 200))
    panel = PanedWindow(win)
    panel.pack(side=TOP, expand=NO, fill=X)
    label = Label(panel, text="I will look for your media files in these folder(s):")
    label.pack(side=LEFT)
    listBox = Listbox(win)
    listBox.pack(expand=YES, fill=BOTH)
    panel = PanedWindow(win)
    scanMyPC = BooleanVar()
    panel.pack(side=TOP, expand=NO, fill=X)
    check = Checkbutton(panel, variable=scanMyPC, command=switch, onvalue=True, offvalue=False, text="Scan my entire PC.")
    check.pack(side=LEFT)
    panel = PanedWindow(win)
    panel.pack(side=TOP, expand=NO, fill=X)
    btn = Button(panel, text="Add Folder", command=add)
    btn.pack(side=LEFT, expand=NO)
    btn = Button(panel, text="Scan now", command=scan)
    btn.pack(side=LEFT, expand=YES, fill=X)
    btn = Button(panel, text="Delete Folder", command=delete)
    btn.pack(side=LEFT, expand=NO)

    create()
    load()

    win.mainloop()

if __name__ == "__main__":
    main()