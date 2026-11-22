"""Which publish slot (if any) should this run fill?  Standard library only, so it runs before anything is installed.

GitHub's cron is best effort: runs can be hours late or skipped. So the workflow runs every hour and this decides:
  - a slot today that is not filled yet and starts within LEAD hours (or was missed) -> fill it
  - otherwise -> nothing to do
A missed slot is published immediately ("now").

    python -m reels.schedule            # prints "<slot> <publish>", e.g. "12:00 12:00", "12:00 now", or "none"
    python -m reels.schedule --force    # manual run: next free slot, however far away
"""
import os, sys, json, datetime as dt

SLOTS = ["12:00", "16:00", "19:00"]      # publish times, IST
LEAD = dt.timedelta(hours=3)             # start making a video up to 3 hours before its slot
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
HISTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state", "history.json")


def slot_time(day, slot):
    hh, mm = map(int, slot.split(":"))
    return dt.datetime(day.year, day.month, day.day, hh, mm, tzinfo=IST)


def due_slot(history, now, force=False):
    """-> (slot, publish) where publish is the slot time or "now" (a missed slot), or None if nothing is due."""
    today = now.date()
    used = {h.get("slot") for h in history if h.get("date") == str(today)}
    for slot in SLOTS:
        if slot in used:
            continue
        at = slot_time(today, slot)
        if at <= now + dt.timedelta(minutes=10):
            return slot, "now"                 # missed (or about to be): publish as soon as it is ready
        if force or at - now <= LEAD:
            return slot, slot
        return None                            # the next free slot is still far away
    return ("extra", "now") if force else None  # all of today's slots are filled


def main():
    try: history = json.load(open(HISTORY, encoding="utf-8"))
    except (OSError, ValueError): history = []
    due = due_slot(history, dt.datetime.now(IST), force="--force" in sys.argv)
    print(" ".join(due) if due else "none")


if __name__ == "__main__":
    main()
