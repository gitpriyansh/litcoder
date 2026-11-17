from config import Config

def compute_month(by_date, first, last, today):
    """by_date maps date -> list of difficulties solved that day.
    Balance is never stored, always computed:
      daily     = DAILY for each day with >= 1 solve
      problems  = POINTS[difficulty] for every solve
      extra     = EXTRA_PER_PROBLEM for each solve beyond the first in a day
      bonus     = BONUS each time the streak reaches STREAK_LEN (then resets)."""
    cells = []
    daily = problem_pts = extra_pts = bonus = run = days_solved = 0
    counts = {"Easy": 0, "Medium": 0, "Hard": 0}
    d = first
    while d <= last:
        diffs = by_date.get(d, [])
        hit = False
        if diffs:
            state = "solved"
            days_solved += 1
            daily += Config.DAILY
            for x in diffs:
                problem_pts += Config.POINTS.get(x, Config.POINTS["Medium"])
                counts[x if x in counts else "Medium"] += 1
            extra_pts += (len(diffs) - 1) * Config.EXTRA_PER_PROBLEM
            run += 1
            if run == Config.STREAK_LEN:
                bonus += Config.BONUS
                run, hit = 0, True
        elif d < today:
            state, run = "missed", 0
        elif d == today:
            state = "pending"
        else:
            state = "future"
        cells.append({"date": d, "state": state, "bonus": hit, "count": len(diffs)})
        d = d.fromordinal(d.toordinal() + 1)
    return {"cells": cells, "daily": daily, "problem_pts": problem_pts,
            "extra_pts": extra_pts, "bonus": bonus,
            "total": daily + problem_pts + extra_pts + bonus,
            "streak": run, "days_solved": days_solved,
            "solved_total": sum(counts.values()), "counts": counts}
