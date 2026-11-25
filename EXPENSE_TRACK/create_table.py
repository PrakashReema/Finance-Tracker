"""
This code will create the tables defined as model
Run it once
"""

from app import app, db

with app.app_context():
    db.create_all()

