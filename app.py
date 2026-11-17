import calendar
from datetime import date, datetime
from zoneinfo import ZoneInfo

from flask import Flask, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from config import Config
from models import Solve, User, db
from services.leetcode import fetch_difficulty, fetch_recent_accepted
from services.rewards import compute_month

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
with app.app_context():
    db.create_all()

def today():
    return datetime.now(ZoneInfo(Config.TIMEZONE)).date()

def month_start(s):
    try:
        y, m = map(int, (s or "").split("-"))
        return date(y, m, 1)
    except ValueError:
        t = today()
        return date(t.year, t.month, 1)

def shift(d, n):
    i = d.year * 12 + d.month - 1 + n
    return date(i // 12, i % 12 + 1, 1)

def add_solve(user, slug, title, d, source, difficulty="Medium"):
    if d < user.start_date:
        return False
    db.session.add(Solve(user_id=user.id, slug=slug, title=title, date=d,
                          source=source, difficulty=difficulty))
    try:
        db.session.commit()
        return True
    except IntegrityError:  # same problem already counted
        db.session.rollback()
        return False

@app.route("/")
def index():
    users = User.query.order_by(User.id).all()
    if len(users) < 2:
        return redirect(url_for("setup"))
    first = month_start(request.args.get("month"))
    last = date(first.year, first.month, calendar.monthrange(first.year, first.month)[1])
    t = today()
    boards = []
    for u in users:
        by_date = {}
        for s in u.solves:
            if first <= s.date <= last:
                by_date.setdefault(s.date, []).append(s.difficulty)
        stats = compute_month(by_date, first, last, t)
        stats["user"] = u
        stats["done_today"] = t in by_date
        stats["today_count"] = len(by_date.get(t, []))
        boards.append(stats)
    a, b = boards[0], boards[1]
    if a["total"] == b["total"]:
        leader = loser = None
    else:
        win, lose = (a, b) if a["total"] > b["total"] else (b, a)
        leader, loser = win["user"], lose["user"]
    return render_template(
        "index.html", boards=boards, first=first, today=t,
        lead_by=abs(a["total"] - b["total"]), leader=leader, loser=loser,
        month_over=t > last, prev=shift(first, -1).strftime("%Y-%m"),
        nxt=shift(first, 1).strftime("%Y-%m"), cfg=Config,
        lead_in=first.weekday(), users=users,
    )

@app.route("/setup", methods=["GET", "POST"])
def setup():
    if User.query.count() >= 2:
        return redirect(url_for("index"))
    if request.method == "POST":
        for i in (1, 2):
            name = request.form.get(f"name{i}", "").strip()
            if name:
                db.session.add(User(name=name, start_date=today(),
                                    leetcode_username=request.form.get(f"lc{i}", "").strip() or None))
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("setup.html")

@app.post("/log")
def log():
    user = db.session.get(User, int(request.form["user_id"]))
    slug = request.form["problem"].strip().lower().replace(" ", "-")
    try:
        d = date.fromisoformat(request.form.get("date") or str(today()))
    except ValueError:
        d = today()
    if not slug:
        flash("Enter a problem name or slug.")
    elif d > today():
        flash("You can't log a future date.")
    elif add_solve(user, slug, slug, d, "manual", request.form.get("difficulty", "Medium")):
        flash(f"Logged {slug} for {user.name}.")
    else:
        flash("Not counted: already logged, or dated before the duel started.")
    return redirect(url_for("index"))

@app.post("/sync")
def sync():
    for u in User.query.all():
        if not u.leetcode_username:
            continue
        try:
            seen = {s.slug for s in u.solves}
            added = 0
            for i in fetch_recent_accepted(u.leetcode_username):
                if i["slug"] in seen or i["date"] < u.start_date:
                    continue
                seen.add(i["slug"])
                added += add_solve(u, i["slug"], i["title"], i["date"], "auto",
                                   fetch_difficulty(i["slug"]))
            flash(f"{u.name}: {added} new solve(s) synced.")
        except Exception as e:
            flash(f"{u.name}: LeetCode sync failed ({type(e).__name__}). Log manually instead.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
