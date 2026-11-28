"""Which Pushpak Katha slot should be filled next? Standard library only (runs before anything is installed).

GitHub's cron is often hours late, so every run fills all free slots of the next 24 hours and YouTube publishes on time.
    python engine/schedule.py            # "<date> <slot> <publish>" or "none"
    python engine/schedule.py --force    # manual run: the next free slot even if it is further away
"""
import os, sys, json, datetime as dt

SLOTS = ["09:00", "14:00", "20:00"]      # publish times, IST (Kanha Ki Paheli uses 12:00, 16:00, 19:00)
LEAD = dt.timedelta(hours=24)
SOON = dt.timedelta(minutes=10)
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY = os.path.join(ROOT, "state", "history.json")


def slot_time(day, slot):
    hh, mm = map(int, slot.split(":")); return dt.datetime(day.year, day.month, day.day, hh, mm, tzinfo=IST)


def due_slot(history, now, force=False):
    """-> (date, slot, publish) with publish = the slot time or "now" (a missed slot), or None."""
    filled = {(h.get("date"), h.get("slot")) for h in history}
    slots = [(str(d), s, slot_time(d, s)) for d in (now.date() + dt.timedelta(days=i) for i in range(4)) for s in SLOTS]
    past = [x for x in slots if x[2] <= now + SOON]; ahead = [x for x in slots if x[2] > now + SOON]
    last = max([i for i, x in enumerate(ahead) if x[:2] in filled], default=-1)
    if past and last < 0 and history and past[-1][:2] not in filled:
        return past[-1][0], past[-1][1], "now"
    for day, slot, at in ahead[last + 1:]:
        return (day, slot, slot) if force or at - now <= LEAD else None
    return None


def load():
    try: return json.load(open(HISTORY, encoding="utf-8"))
    except (OSError, ValueError): return []


if __name__ == "__main__":
    due = due_slot(load(), dt.datetime.now(IST), force="--force" in sys.argv)
    print(" ".join(due) if due else "none")
