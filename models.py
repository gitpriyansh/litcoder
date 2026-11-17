from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    leetcode_username = db.Column(db.String(80))
    start_date = db.Column(db.Date, nullable=False)  # solves before this are ignored
    solves = db.relationship("Solve", backref="user", cascade="all, delete-orphan")

class Solve(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    slug = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200))
    source = db.Column(db.String(10), default="manual")  # 'auto' or 'manual'
    difficulty = db.Column(db.String(10), default="Medium")  # Easy / Medium / Hard
    __table_args__ = (db.UniqueConstraint("user_id", "slug", name="uq_user_problem"),)
