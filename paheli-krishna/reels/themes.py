"""Looks. Every series gets the next theme of its format, so all its parts match and the next series looks different.

THEME is the look of the reel being rendered (render.start() sets it in every process). A theme only lists what differs
from the BASE of its format; theme 0 is the original look.
    ui:    caption / hook / card colours             tint: colour grade
    cut:   fade | slide | zoom (shot transition)     music: pitch factor of the background music
    people: clothes per character
"""
from .util import darker

UI = dict(hl=(255, 212, 0), accent=(245, 195, 60), panel=(25, 12, 40), ink=(60, 20, 30), hook_bg=(255, 255, 255), hook_fg=(25, 20, 30),
          hook_hl=(214, 30, 50), paper=(250, 236, 205), paper_fg=(150, 24, 36), button=(240, 40, 80), radius=22)
COMMON = dict(ui=UI, tint=(1.03, 1.0, 0.95), cut="fade", music=1.0, people={})

BASE = {
    "paheli": dict(
        COMMON, wall=((58, 12, 22), (124, 32, 40), (148, 50, 44)), arch=(72, 18, 30), gold=(236, 180, 70), banner=(200, 40, 50),
        throne=(176, 26, 40), gem=(60, 160, 220), floor=((186, 146, 108), (222, 186, 140)), tiles="planks", carpet=(190, 30, 44),
        view=None, fan=None, flip=False),
    "devotional": dict(
        COMMON, sky=((92, 140, 205), (200, 190, 200), (255, 214, 168), (255, 222, 175)), sun=((255, 236, 190), (255, 250, 230)),
        sun_xy=(860, 560), hills=(206, 170, 170), far=(150, 150, 130), leaf=((40, 90, 50), (72, 130, 64), (130, 175, 80)),
        ground=((170, 190, 100), (66, 110, 46)), path=(228, 196, 146), haze=(255, 225, 170), rays=60, fog=(235, 215, 190),
        petal=(150, 200, 90), divine=((255, 242, 195), (252, 190, 100), (196, 84, 96), (64, 28, 84)), stars=False),
}


def _ui(**k):
    return {**UI, **k}


def _court(king, guard, sash, chatur=(246, 238, 216), border=(226, 120, 40)):
    """Clothes of the court: the king's colour, the guards' colour, Chatur's sash and kurta."""
    light = lambda c, n: tuple(min(255, x + n) for x in c)
    return dict(R=dict(dhoti=king, pleat=light(king, 22), top=king, legs=king, cape=darker(king, 0.7)),
                G=dict(dhoti=guard, pleat=light(guard, 18), border=darker(guard, 0.75), legs=guard),
                C=dict(sash=sash, top=chatur, border=border, dhoti=chatur, pleat=light(chatur, 10), legs=chatur))


def _man(top, dhoti):
    return dict(P=dict(top=top, dhoti=dhoti, pleat=tuple(min(255, c + 14) for c in dhoti), border=darker(dhoti, 0.75)))


BLUE = _ui(hl=(110, 225, 255), accent=(130, 200, 255), panel=(8, 18, 58), ink=(10, 24, 70), hook_bg=(22, 34, 96), hook_fg=(255, 255, 255),
           hook_hl=(110, 225, 255), paper=(226, 236, 255), paper_fg=(28, 48, 140), button=(40, 110, 240), radius=52)
GREEN = _ui(hl=(170, 255, 110), accent=(160, 230, 120), panel=(8, 44, 30), ink=(12, 60, 36), hook_bg=(16, 92, 60), hook_fg=(255, 255, 255),
            hook_hl=(255, 226, 90), paper=(240, 250, 226), paper_fg=(16, 96, 60), button=(240, 130, 20), radius=8)
PURPLE = _ui(hl=(255, 150, 220), accent=(255, 160, 215), panel=(44, 10, 64), ink=(74, 16, 84), hook_bg=(250, 226, 250), hook_fg=(60, 16, 84),
             hook_hl=(220, 30, 130), paper=(250, 232, 250), paper_fg=(124, 30, 140), button=(190, 40, 200), radius=40)
ORANGE = _ui(hl=(255, 176, 50), accent=(255, 170, 60), panel=(60, 30, 14), ink=(80, 40, 10), hook_bg=(240, 126, 30), hook_fg=(255, 255, 255),
             hook_hl=(90, 24, 0), paper=(255, 246, 232), paper_fg=(180, 80, 10), button=(220, 60, 30), radius=52)
TEAL = _ui(hl=(80, 240, 220), accent=(90, 220, 210), panel=(8, 34, 40), ink=(6, 50, 56), hook_bg=(20, 26, 30), hook_fg=(255, 255, 255),
           hook_hl=(80, 240, 220), paper=(232, 244, 240), paper_fg=(10, 92, 100), button=(0, 150, 150), radius=8)
PINK = _ui(hl=(255, 170, 205), accent=(255, 170, 200), panel=(70, 14, 50), ink=(90, 16, 56), hook_bg=(255, 228, 238), hook_fg=(80, 16, 54),
           hook_hl=(222, 30, 110), paper=(255, 236, 242), paper_fg=(170, 24, 90), button=(232, 50, 130), radius=40)
AMBER = _ui(hl=(255, 200, 70), accent=(250, 190, 80), panel=(54, 30, 10), ink=(74, 40, 8), hook_bg=(250, 236, 206), hook_fg=(70, 36, 10),
            hook_hl=(200, 80, 0), paper=(252, 240, 214), paper_fg=(150, 70, 10), button=(200, 80, 20), radius=40)

THEMES = {
    "paheli": [
        dict(),                                                                                        # red court
        dict(wall=((10, 16, 48), (24, 42, 104), (40, 62, 128)), arch=(14, 22, 60), gold=(226, 190, 104), banner=(40, 80, 190),       # blue night
             throne=(34, 52, 150), gem=(240, 70, 90), floor=((96, 104, 140), (156, 164, 196)), tiles="checker", carpet=(36, 58, 160),
             view="night", fan=(90, 130, 230), flip=True, tint=(0.97, 1.0, 1.06), cut="slide", music=0.89, ui=BLUE,
             people=_court((36, 62, 170), (40, 52, 96), (60, 110, 220), border=(60, 110, 220))),
        dict(wall=((16, 52, 40), (44, 110, 80), (84, 146, 104)), arch=(20, 66, 50), gold=(240, 206, 110), banner=(34, 140, 90),      # green garden
             throne=(20, 104, 74), gem=(250, 120, 60), floor=((206, 196, 172), (240, 232, 212)), tiles="checker", carpet=(26, 124, 84),
             view="garden", tint=(1.02, 1.02, 0.95), cut="zoom", music=1.12, ui=GREEN,
             people=_court((22, 128, 84), (90, 70, 40), (240, 160, 30), border=(22, 128, 84))),
        dict(wall=((38, 14, 62), (92, 40, 128), (132, 68, 150)), arch=(50, 18, 78), gold=(246, 200, 120), banner=(220, 60, 140),     # purple sunset
             throne=(120, 40, 150), gem=(80, 230, 200), floor=((150, 120, 168), (206, 180, 214)), carpet=(122, 36, 150),
             view="sunset", fan=(230, 90, 170), flip=True, tint=(1.03, 0.98, 1.02), cut="slide", music=0.94, ui=PURPLE,
             people=_court((132, 44, 160), (70, 34, 90), (226, 60, 140), border=(226, 60, 140))),
        dict(wall=((150, 142, 136), (206, 196, 182), (222, 212, 194)), arch=(150, 140, 136), gold=(214, 156, 60), banner=(240, 130, 40),  # marble
             throne=(220, 110, 40), gem=(40, 120, 220), floor=((184, 180, 176), (226, 222, 216)), tiles="checker", carpet=(226, 120, 40),
             view="garden", tint=(1.0, 1.0, 1.0), music=1.06, ui=ORANGE,
             people=_court((232, 130, 34), (110, 60, 40), (40, 120, 190), chatur=(190, 216, 236), border=(40, 120, 190))),
        dict(wall=((30, 34, 38), (72, 74, 74), (104, 100, 92)), arch=(32, 34, 40), gold=(198, 150, 80), banner=(24, 130, 140),       # stone fort
             throne=(20, 92, 104), gem=(250, 180, 50), floor=((110, 104, 96), (160, 150, 134)), carpet=(24, 110, 120),
             view="night", flip=True, tint=(1.04, 1.0, 0.93), cut="zoom", music=0.84, ui=TEAL,
             people=_court((24, 120, 130), (64, 64, 70), (210, 60, 40), chatur=(232, 214, 168), border=(150, 70, 30))),
    ],
    "devotional": [
        dict(),                                                                                        # morning
        dict(sky=((8, 14, 48), (22, 38, 92), (52, 74, 138), (84, 104, 160)), sun=((170, 190, 240), (245, 248, 255)), sun_xy=(820, 420),  # moonlight
             hills=(50, 66, 118), far=(36, 60, 84), leaf=((14, 46, 58), (28, 80, 84), (70, 130, 130)), ground=((62, 104, 108), (20, 48, 60)),
             path=(128, 140, 168), haze=(120, 150, 220), rays=18, fog=(60, 80, 130), petal=(160, 200, 240), stars=True,
             divine=((235, 245, 255), (130, 180, 250), (60, 80, 190), (16, 16, 70)), tint=(0.95, 1.0, 1.08), cut="slide", music=0.89, ui=BLUE,
             people=_man((150, 160, 190), (92, 84, 120))),
        dict(sky=((150, 200, 240), (214, 224, 244), (255, 224, 230), (255, 232, 226)), hills=(214, 180, 206), far=(190, 160, 170),    # spring blossom
             leaf=((176, 70, 116), (236, 124, 168), (255, 190, 214)), ground=((178, 206, 120), (92, 142, 70)), path=(240, 216, 190),
             haze=(255, 222, 230), rays=45, fog=(246, 222, 230), petal=(255, 160, 196),
             divine=((255, 246, 240), (255, 180, 200), (210, 90, 150), (84, 30, 96)), tint=(1.02, 1.0, 1.0), cut="zoom", music=1.12, ui=PINK,
             people=_man((222, 196, 150), (110, 84, 110))),
        dict(sky=((70, 40, 104), (176, 72, 104), (250, 130, 72), (255, 190, 100)), sun=((255, 170, 90), (255, 236, 180)), sun_xy=(300, 800),  # sunset
             hills=(130, 64, 92), far=(96, 58, 62), leaf=((70, 48, 36), (124, 82, 44), (206, 130, 56)), ground=((176, 130, 66), (84, 64, 34)),
             path=(230, 168, 110), haze=(255, 170, 100), rays=70, fog=(226, 150, 110), petal=(250, 150, 60),
             divine=((255, 236, 180), (255, 150, 70), (190, 50, 60), (60, 14, 50)), tint=(1.06, 0.99, 0.92), cut="slide", music=0.94, ui=ORANGE,
             people=_man((206, 170, 120), (140, 70, 50))),
        dict(sky=((56, 150, 230), (130, 200, 244), (206, 236, 244), (230, 244, 226)), sun=((255, 250, 210), (255, 255, 240)), sun_xy=(220, 420),  # green noon
             hills=(130, 180, 170), far=(96, 150, 100), leaf=((16, 92, 44), (44, 150, 62), (130, 206, 80)), ground=((150, 206, 90), (44, 120, 46)),
             path=(226, 206, 160), haze=(236, 250, 210), rays=40, fog=(206, 234, 220), petal=(255, 220, 80),
             divine=((250, 255, 225), (160, 230, 140), (30, 140, 110), (8, 50, 64)), tint=(1.0, 1.02, 0.98), cut="zoom", music=1.06, ui=GREEN,
             people=_man((170, 200, 170), (96, 104, 70))),
        dict(sky=((120, 150, 176), (206, 200, 190), (246, 222, 180), (250, 228, 190)), hills=(190, 160, 140), far=(170, 130, 90),     # autumn
             leaf=((140, 56, 20), (214, 110, 30), (250, 190, 70)), ground=((206, 176, 96), (130, 96, 46)), path=(236, 210, 166),
             haze=(255, 226, 170), rays=55, fog=(236, 212, 176), petal=(236, 130, 30), sun_xy=(700, 480),
             divine=((255, 246, 200), (250, 200, 80), (170, 100, 30), (60, 34, 20)), tint=(1.04, 1.0, 0.93), music=0.84, ui=AMBER,
             people=_man((200, 150, 100), (90, 96, 110))),
    ],
}

THEME = {}


def use(kind, n):
    """Make theme n of this format the current look."""
    THEME.clear()
    THEME.update(BASE[kind])
    THEME.update(THEMES[kind][n % len(THEMES[kind])])
