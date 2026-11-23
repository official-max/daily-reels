"""Which publish slot should be filled next?  Standard library only, so it runs before anything is installed.

GitHub's cron is best effort: runs can be many hours late or skipped. So every run fills all the free slots of the
next 24 hours and YouTube does the publishing on time; one run a day, at any hour, is enough.
A slot that was missed today is filled at once ("now"), but only the latest one, so videos never come out in a bunch.

    python -m reels.schedule            # prints "<date> <slot> <publish>", e.g. "2026-11-23 12:00 12:00", or "none"
    python -m reels.schedule --force    # manual run: the next free slot even if it is more than 24 hours away
"""
import os, sys, json, datetime as dt

SLOTS = ["12:00", "16:00", "19:00"]      # publish times, IST
LEAD = dt.timedelta(hours=24)            # fill slots up to this far ahead
SOON = dt.timedelta(minutes=10)          # closer than this counts as missed: too late to schedule on YouTube
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
HISTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state", "history.json")


def slot_time(day, slot):
    hh, mm = map(int, slot.split(":"))
    return dt.datetime(day.year, day.month, day.day, hh, mm, tzinfo=IST)


def due_slot(history, now, force=False):
    """-> (date, slot, publish) where publish is the slot time or "now" (a missed slot), or None if nothing is due.

    Slots are filled in time order, after everything already scheduled, so the parts of a story stay in order."""
    filled = {(h.get("date"), h.get("slot")) for h in history}
    days = [now.date() + dt.timedelta(days=i) for i in range(4)]
    slots = [(str(d), s, slot_time(d, s)) for d in days for s in SLOTS]
    past = [x for x in slots if x[2] <= now + SOON]
    ahead = [x for x in slots if x[2] > now + SOON]
    last = max([i for i, x in enumerate(ahead) if x[:2] in filled], default=-1)
    if past and last < 0 and past[-1][:2] not in filled:
        return past[-1][0], past[-1][1], "now"
    for day, slot, at in ahead[last + 1:]:
        return (day, slot, slot) if force or at - now <= LEAD else None
    return None


def main():
    try: history = json.load(open(HISTORY, encoding="utf-8"))
    except (OSError, ValueError): history = []
    due = due_slot(history, dt.datetime.now(IST), force="--force" in sys.argv)
    print(" ".join(due) if due else "none")


if __name__ == "__main__":
    main()
