"""All settings in one place: video size, paths, voices, speaker names and the story formats."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")
STATE = os.path.join(ROOT, "state")
SPRITE_DIR = os.path.join(os.environ.get("LOCALAPPDATA", OUT), "reel_sprites")   # character layer cache
os.makedirs(SPRITE_DIR, exist_ok=True)

# ---- video
W, H, FPS = 1080, 1920, 30
SS = 2              # everything is drawn at 2x and scaled down (smooth edges)
SR = 44100          # audio sample rate
GAP = 0.3           # pause between two lines of the same shot (s)
XF = 0.35           # crossfade between shots (s)

FONT_CAP = os.path.join(ROOT, "fonts", "Poppins-Black.ttf")
FONT_B = os.path.join(ROOT, "fonts", "Poppins-Bold.ttf")

# ---- speakers: edge-tts voice, rate, pitch
VOICES = {
    "N": ("hi-IN-SwaraNeural", "-4%", "+0Hz"),     # narrator
    "K": ("hi-IN-MadhurNeural", "-10%", "-4Hz"),   # Shri Krishna (gets a soft reverb)
    "A": ("hi-IN-MadhurNeural", "+0%", "+6Hz"),    # Arjun
    "P": ("hi-IN-MadhurNeural", "-12%", "-10Hz"),  # ordinary man
    "R": ("hi-IN-MadhurNeural", "-8%", "-14Hz"),   # Raja
    "C": ("hi-IN-MadhurNeural", "+4%", "+3Hz"),    # Chatur, the clever man
}
# caption tag shown above a character's lines: (default name, colour). The narrator has no tag.
TAGS = {"K": ("Shri Krishna", (45, 100, 205)), "A": ("Arjun", (165, 40, 55)), "P": ("Garib vyakti", (125, 88, 52)),
        "R": ("Raja", (176, 28, 44)), "C": ("Chatur", (205, 110, 30))}
BLINK_OFF = dict(K=0.0, A=1.3, P=2.2, R=0.5, C=1.8, G=2.9)   # so characters don't blink in sync

# ---- story formats. Adding a format = add an entry here + its scene(s) in scenes.py + a section in writer.PROMPT.
FORMATS = {
    "paheli": dict(
        parts=2, label="PAHELI",
        scenes=("darbar",), default_scene="darbar", speakers=("N", "R", "C"), named="C",   # p_name is shown as C's caption tag
    ),
    "devotional": dict(
        parts=3, label="KRISHNA KATHA",
        scenes=("walk", "meet", "divine"), default_scene="meet", speakers=("N", "K", "A", "P"), named="P",
    ),
}
KINDS = tuple(FORMATS)          # rotation order: paheli -> devotional -> paheli ...
MOODS = ("sad", "neutral", "happy", "angry", "shock")
ICONS = ("gallows", "sword", "question", "tick", "cross", "coin", "door", "lamp", "crown", "clock")
