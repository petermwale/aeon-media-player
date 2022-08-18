from sys import platform
from os import access, R_OK
from pygame.display import get_wm_info
from pygame.mixer import quit as Quit
from vlc import Instance, EventType
from widget import Widget


class Movie(Widget):
    """Controls video playback"""

    def __init__(self, parent):
        super(Movie, self).__init__(parent)
        self.vlcInstance = Instance()
        self.player = self.vlcInstance.media_player_new()

        em = self.player.event_manager()
        em.event_attach(EventType.MediaPlayerTimeChanged, self.callback, self.player)

        win_id = get_wm_info()["window"]

        if "win" in platform:
            self.player.set_hwnd(win_id)
        elif "linux" in platform:
            self.player.set_xwindow(win_id)
        elif "darwin" in platform:
            self.player.set_agl(win_id)

    def callback(self, event, player):
        #print(player.get_fps()
        self.parent.controls.seeker.config({"to": self.player.get_length()})
        self.parent.controls.seeker.setValue(self.player.get_time())

    def play(self, video):
        if not access(video, R_OK):
            print(f"ERROR: Cannot play video '{video}', not accessible.")
            return
        media = self.vlcInstance.media_new(video)
        self.player.set_media(media)
        Quit()
        self.player.play()