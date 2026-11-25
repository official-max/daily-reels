# Pushpak Katha

Valmiki Ramayan, adhyay-dar-adhyay, animated Hindi Shorts. Channel: https://www.youtube.com/@PushpakKatha

- `engine/`: drawing and animation (Skia). `rig.py` action rig, `puppet.py` puppets, `toon.py` animals, `chibi.py` painted chibi, `lab.py` voices, captions, sound, encoding.
- `plan/ramayan.json`: all 732 parts in story order. `plan/channel.json`: series and start date.
- `state/`: what has been posted (used once the automation exists).
- `ramayan_01.md`: script of part 1. `brand/`: logo and banner.
- Output goes to `out/` (not in git). Run: `python engine/hanuman.py preview`
