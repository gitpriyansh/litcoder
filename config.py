import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = "sqlite:///duel.db"
    TIMEZONE = "Asia/Kolkata"   # what counts as "a day"
    DAILY = 10                  # Rs per day with >= 1 solve
    STREAK_LEN = 7              # streak length that triggers the bonus
    BONUS = 70                  # Rs bonus on every completed streak
    POINTS = {"Easy": 1, "Medium": 2, "Hard": 5}  # Rs per solved problem
    EXTRA_PER_PROBLEM = 2       # Rs for each problem beyond the first in a day
